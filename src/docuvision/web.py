"""Browser upload UI for DocuVision."""

from __future__ import annotations

import argparse
from email.parser import BytesParser
from email.policy import default
import json
import mimetypes
import os
import sys
import uuid
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from .cli import run


ROOT = Path(__file__).resolve().parents[2]
OUTPUTS = ROOT / "outputs"
UPLOADS = OUTPUTS / "uploads"
UI_RUNS = OUTPUTS / "ui"
MAX_UPLOAD_BYTES = 12 * 1024 * 1024
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}


INDEX_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>DocuVision AI — Intelligent Document Scanner & Quality Engine</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Fira+Code:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-base: #06090e;
      --bg-surface: rgba(15, 23, 38, 0.78);
      --bg-card: rgba(18, 28, 45, 0.65);
      --bg-input: rgba(10, 16, 26, 0.9);
      --border-glow: rgba(16, 185, 129, 0.35);
      --border-subtle: rgba(255, 255, 255, 0.09);
      --border-accent: rgba(6, 182, 212, 0.45);
      --accent-emerald: #10b981;
      --accent-cyan: #06b6d4;
      --accent-violet: #8b5cf6;
      --accent-amber: #f59e0b;
      --accent-rose: #f43f5e;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --text-dim: #64748b;
      --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      --font-mono: 'Fira Code', monospace;
      --glass-blur: blur(20px);
      --shadow-glow: 0 0 35px rgba(16, 185, 129, 0.18);
      --shadow-card: 0 12px 36px -10px rgba(0, 0, 0, 0.6);
    }

    *, *::before, *::after {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      background-color: var(--bg-base);
      color: var(--text-main);
      font-family: var(--font-sans);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      overflow-x: hidden;
      background-image: 
        linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px),
        radial-gradient(circle at 15% 15%, rgba(16, 185, 129, 0.1) 0%, transparent 45%),
        radial-gradient(circle at 85% 20%, rgba(6, 182, 212, 0.1) 0%, transparent 50%),
        radial-gradient(circle at 50% 85%, rgba(139, 92, 246, 0.08) 0%, transparent 55%);
      background-size: 32px 32px, 32px 32px, auto, auto, auto;
      background-attachment: fixed;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: rgba(10, 16, 26, 0.5); }
    ::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.18); border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--accent-emerald); }

    /* Shell & Header */
    .app-header {
      position: sticky;
      top: 0;
      z-index: 100;
      background: rgba(6, 9, 14, 0.88);
      backdrop-filter: var(--glass-blur);
      border-bottom: 1px solid var(--border-subtle);
      padding: 14px 28px;
    }

    .header-inner {
      max-width: 1400px;
      margin: 0 auto;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      width: 100%;
    }

    .brand-logo {
      display: flex;
      align-items: center;
      gap: 12px;
      text-decoration: none;
      color: var(--text-main);
    }

    .brand-icon-box {
      width: 42px;
      height: 42px;
      border-radius: 12px;
      background: linear-gradient(135deg, rgba(16, 185, 129, 0.25), rgba(6, 182, 212, 0.25));
      border: 1px solid var(--border-glow);
      display: grid;
      place-items: center;
      color: var(--accent-emerald);
      box-shadow: 0 0 15px rgba(16, 185, 129, 0.25);
    }

    .brand-title {
      font-size: 20px;
      font-weight: 800;
      letter-spacing: -0.02em;
      background: linear-gradient(135deg, #ffffff 30%, #a7f3d0 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .brand-tag {
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      padding: 3px 8px;
      border-radius: 6px;
      background: rgba(16, 185, 129, 0.12);
      color: var(--accent-emerald);
      border: 1px solid rgba(16, 185, 129, 0.3);
    }

    .status-badge {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 6px 14px;
      border-radius: 30px;
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      font-size: 13px;
      font-weight: 600;
      color: var(--text-muted);
    }

    .status-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--accent-emerald);
      box-shadow: 0 0 8px var(--accent-emerald);
      animation: pulse 2s infinite;
    }

    .status-dot.busy {
      background: var(--accent-amber);
      box-shadow: 0 0 8px var(--accent-amber);
    }

    @keyframes pulse {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.5; transform: scale(0.85); }
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .btn-quick-demo {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 16px;
      border-radius: 10px;
      background: rgba(6, 182, 212, 0.14);
      border: 1px solid var(--border-accent);
      color: var(--accent-cyan);
      font-size: 13px;
      font-weight: 700;
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .btn-quick-demo:hover {
      background: rgba(6, 182, 212, 0.25);
      transform: translateY(-1px);
      box-shadow: 0 4px 18px rgba(6, 182, 212, 0.25);
    }

    .shortcut-pill {
      font-size: 12px;
      color: var(--text-dim);
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--border-subtle);
      padding: 4px 8px;
      border-radius: 6px;
    }

    /* Main Container Layout */
    .main-wrapper {
      max-width: 1400px;
      width: 100%;
      margin: 0 auto;
      padding: 28px 24px 60px;
      flex: 1;
    }

    .grid-container {
      display: grid;
      grid-template-columns: 380px 1fr;
      gap: 24px;
      align-items: start;
      width: 100%;
    }

    /* Glass Panels */
    .glass-panel {
      width: 100%;
      background: var(--bg-surface);
      backdrop-filter: var(--glass-blur);
      border: 1px solid var(--border-subtle);
      border-radius: 18px;
      box-shadow: var(--shadow-card);
      transition: border-color 0.2s ease;
      overflow: hidden;
      box-sizing: border-box;
    }

    .glass-panel:hover {
      border-color: rgba(255, 255, 255, 0.15);
    }

    .panel-header {
      width: 100%;
      padding: 18px 22px;
      border-bottom: 1px solid var(--border-subtle);
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: rgba(10, 16, 26, 0.5);
      box-sizing: border-box;
    }

    .panel-title {
      font-size: 15px;
      font-weight: 700;
      letter-spacing: -0.01em;
      color: var(--text-main);
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .panel-title svg {
      color: var(--accent-emerald);
    }

    .panel-body {
      width: 100%;
      padding: 24px;
      box-sizing: border-box;
    }

    /* Form Container */
    #uploadForm {
      width: 100%;
      display: flex;
      flex-direction: column;
      align-items: stretch;
      box-sizing: border-box;
    }

    /* Dropzone Studio - PERFECT FULL-WIDTH BORDER */
    .dropzone-studio {
      width: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 230px;
      border: 2px dashed rgba(16, 185, 129, 0.45);
      border-radius: 16px;
      background: var(--bg-input);
      padding: 32px 20px;
      text-align: center;
      cursor: pointer;
      position: relative;
      overflow: hidden;
      box-sizing: border-box;
      transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .dropzone-studio:hover,
    .dropzone-studio.dragover {
      border-color: var(--accent-emerald);
      background: rgba(16, 185, 129, 0.08);
      box-shadow: inset 0 0 20px rgba(16, 185, 129, 0.15), 0 0 22px rgba(16, 185, 129, 0.22);
    }

    .dropzone-studio input[type="file"] {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      opacity: 0;
      cursor: pointer;
      z-index: 10;
    }

    .upload-icon-ring {
      width: 64px;
      height: 64px;
      margin: 0 auto 14px;
      border-radius: 50%;
      background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(6, 182, 212, 0.2));
      border: 1px solid var(--border-glow);
      display: grid;
      place-items: center;
      color: var(--accent-emerald);
      transition: transform 0.3s ease;
      z-index: 2;
    }

    .dropzone-studio:hover .upload-icon-ring {
      transform: scale(1.08) translateY(-2px);
    }

    .drop-heading {
      font-size: 15px;
      font-weight: 700;
      color: var(--text-main);
      margin-bottom: 6px;
      z-index: 2;
    }

    .drop-sub {
      font-size: 13px;
      color: var(--text-muted);
      z-index: 2;
    }

    .drop-sub span {
      color: var(--accent-emerald);
      font-weight: 600;
    }

    /* Selected File Preview Card */
    .file-preview-card {
      width: 100%;
      margin-top: 18px;
      padding: 12px;
      border-radius: 12px;
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid var(--border-subtle);
      display: flex;
      align-items: center;
      gap: 12px;
      box-sizing: border-box;
    }

    .file-thumb-box {
      width: 46px;
      height: 46px;
      border-radius: 8px;
      background: #000;
      overflow: hidden;
      flex-shrink: 0;
      border: 1px solid var(--border-subtle);
      display: grid;
      place-items: center;
    }

    .file-thumb-box img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }

    .file-meta {
      flex: 1;
      min-width: 0;
    }

    .file-name {
      font-size: 13px;
      font-weight: 600;
      color: var(--text-main);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .file-size {
      font-size: 12px;
      color: var(--text-dim);
      margin-top: 2px;
    }

    /* Primary Action Buttons */
    .btn-scan-primary {
      width: 100%;
      height: 48px;
      margin-top: 18px;
      border-radius: 12px;
      border: 0;
      background: linear-gradient(135deg, #10b981 0%, #06b6d4 100%);
      color: #041215;
      font-family: var(--font-sans);
      font-weight: 800;
      font-size: 15px;
      letter-spacing: 0.01em;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      box-shadow: 0 4px 20px rgba(16, 185, 129, 0.35);
      transition: all 0.25s ease;
      box-sizing: border-box;
    }

    .btn-scan-primary:hover:not(:disabled) {
      transform: translateY(-2px);
      box-shadow: 0 6px 28px rgba(16, 185, 129, 0.5);
      filter: brightness(1.08);
    }

    .btn-scan-primary:disabled {
      opacity: 0.45;
      cursor: not-allowed;
      box-shadow: none;
      transform: none;
    }

    .btn-preset-panel {
      width: 100%;
      height: 42px;
      margin-top: 10px;
      border-radius: 10px;
      border: 1px solid var(--border-accent);
      background: rgba(6, 182, 212, 0.08);
      color: var(--accent-cyan);
      font-family: var(--font-sans);
      font-weight: 700;
      font-size: 13px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      transition: all 0.2s ease;
      box-sizing: border-box;
    }

    .btn-preset-panel:hover {
      background: rgba(6, 182, 212, 0.18);
      border-color: var(--accent-cyan);
    }

    /* Feature List */
    .feature-list {
      margin-top: 22px;
      border-top: 1px solid var(--border-subtle);
      padding-top: 18px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      width: 100%;
    }

    .feature-item {
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 13px;
      color: var(--text-muted);
    }

    .feature-item svg {
      color: var(--accent-emerald);
      flex-shrink: 0;
    }

    /* Workspace & Tabs */
    .workspace-tabs-bar {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      background: var(--bg-surface);
      backdrop-filter: var(--glass-blur);
      border: 1px solid var(--border-subtle);
      border-radius: 14px;
      margin-bottom: 20px;
      overflow-x: auto;
      width: 100%;
      box-sizing: border-box;
    }

    .tab-btn {
      padding: 10px 18px;
      border-radius: 10px;
      border: 0;
      background: transparent;
      color: var(--text-muted);
      font-family: var(--font-sans);
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 8px;
      transition: all 0.2s ease;
      white-space: nowrap;
    }

    .tab-btn:hover {
      color: var(--text-main);
      background: rgba(255, 255, 255, 0.04);
    }

    .tab-btn.active {
      background: rgba(16, 185, 129, 0.15);
      color: #ffffff;
      border: 1px solid rgba(16, 185, 129, 0.35);
      box-shadow: 0 0 15px rgba(16, 185, 129, 0.12);
    }

    .tab-btn.active svg {
      color: var(--accent-emerald);
    }

    /* Tab Content Panels */
    .tab-content {
      display: none;
      width: 100%;
    }

    .tab-content.active {
      display: block;
      animation: fadeIn 0.3s ease;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(6px); }
      to { opacity: 1; transform: translateY(0); }
    }

    /* Display Views & Cards */
    .result-display-card {
      position: relative;
      width: 100%;
      border-radius: 16px;
      background: var(--bg-surface);
      backdrop-filter: var(--glass-blur);
      border: 1px solid var(--border-subtle);
      overflow: hidden;
      box-shadow: var(--shadow-card);
      box-sizing: border-box;
    }

    .display-preview-area {
      width: 100%;
      min-height: 500px;
      max-height: 680px;
      background: #030508;
      display: grid;
      place-items: center;
      position: relative;
      overflow: hidden;
    }

    .display-preview-area img {
      max-width: 100%;
      max-height: 680px;
      object-fit: contain;
      border-radius: 4px;
      box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6);
      transition: transform 0.3s ease;
    }

    .empty-state-box {
      text-align: center;
      padding: 60px 20px;
      color: var(--text-dim);
    }

    .empty-icon {
      width: 64px;
      height: 64px;
      margin: 0 auto 16px;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid var(--border-subtle);
      display: grid;
      place-items: center;
      color: var(--text-dim);
    }

    .display-actions-bar {
      padding: 16px 22px;
      background: rgba(10, 16, 26, 0.85);
      border-top: 1px solid var(--border-subtle);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 14px;
      width: 100%;
      box-sizing: border-box;
    }

    .btn-action-outline {
      padding: 9px 18px;
      border-radius: 10px;
      border: 1px solid var(--border-subtle);
      background: rgba(255, 255, 255, 0.04);
      color: var(--text-main);
      font-family: var(--font-sans);
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 8px;
      text-decoration: none;
      transition: all 0.2s ease;
    }

    .btn-action-outline:hover:not([aria-disabled="true"]):not(:disabled) {
      background: rgba(255, 255, 255, 0.1);
      border-color: rgba(255, 255, 255, 0.2);
    }

    .btn-action-outline[aria-disabled="true"],
    .btn-action-outline:disabled {
      opacity: 0.4;
      cursor: not-allowed;
      pointer-events: none;
    }

    .btn-action-primary {
      padding: 9px 20px;
      border-radius: 10px;
      border: 0;
      background: var(--accent-emerald);
      color: #041215;
      font-family: var(--font-sans);
      font-size: 13px;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 8px;
      text-decoration: none;
      transition: all 0.2s ease;
    }

    .btn-action-primary:hover:not([aria-disabled="true"]) {
      background: #34d399;
      transform: translateY(-1px);
    }

    .btn-action-primary[aria-disabled="true"] {
      opacity: 0.4;
      cursor: not-allowed;
      pointer-events: none;
    }

    /* Quality Metrics Grid */
    .quality-dashboard {
      display: flex;
      flex-direction: column;
      gap: 20px;
      width: 100%;
    }

    .verdict-banner {
      padding: 20px 24px;
      border-radius: 14px;
      background: rgba(16, 185, 129, 0.08);
      border: 1px solid rgba(16, 185, 129, 0.25);
      display: flex;
      align-items: center;
      gap: 16px;
      width: 100%;
      box-sizing: border-box;
    }

    .verdict-banner.review {
      background: rgba(245, 158, 11, 0.08);
      border-color: rgba(245, 158, 11, 0.25);
    }

    .verdict-badge {
      padding: 6px 14px;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 800;
      letter-spacing: 0.05em;
    }

    .verdict-badge.pass {
      background: rgba(16, 185, 129, 0.2);
      color: #34d399;
      border: 1px solid rgba(52, 211, 153, 0.4);
    }

    .verdict-badge.review {
      background: rgba(245, 158, 11, 0.2);
      color: #fbbf24;
      border: 1px solid rgba(251, 191, 36, 0.4);
    }

    .verdict-text {
      font-size: 14px;
      color: var(--text-muted);
      line-height: 1.5;
    }

    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 16px;
      width: 100%;
    }

    .metric-card {
      padding: 18px;
      border-radius: 14px;
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      box-sizing: border-box;
    }

    .metric-top {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 12px;
    }

    .metric-label-text {
      font-size: 13px;
      font-weight: 600;
      color: var(--text-muted);
    }

    .metric-status-tag {
      font-size: 11px;
      font-weight: 700;
      padding: 2px 7px;
      border-radius: 4px;
      background: rgba(255, 255, 255, 0.05);
      color: var(--text-dim);
    }

    .metric-status-tag.ok {
      background: rgba(16, 185, 129, 0.12);
      color: #34d399;
    }

    .metric-val-num {
      font-size: 26px;
      font-weight: 800;
      color: var(--text-main);
      letter-spacing: -0.02em;
      margin-bottom: 12px;
    }

    .metric-progress-track {
      width: 100%;
      height: 6px;
      border-radius: 3px;
      background: rgba(255, 255, 255, 0.06);
      overflow: hidden;
    }

    .metric-progress-fill {
      height: 100%;
      border-radius: 3px;
      background: linear-gradient(90deg, var(--accent-emerald), var(--accent-cyan));
      width: 0%;
      transition: width 0.6s ease;
    }

    /* JSON View */
    .json-code-box {
      font-family: var(--font-mono);
      font-size: 13px;
      line-height: 1.6;
      color: #a7f3d0;
      background: #03060a;
      padding: 20px;
      border-radius: 12px;
      border: 1px solid var(--border-subtle);
      max-height: 500px;
      overflow-y: auto;
      white-space: pre-wrap;
      word-break: break-all;
      width: 100%;
      box-sizing: border-box;
    }

    /* Toast Notification */
    .toast-container {
      position: fixed;
      bottom: 24px;
      right: 24px;
      z-index: 2000;
      display: flex;
      flex-direction: column;
      gap: 10px;
      pointer-events: none;
    }

    .toast {
      pointer-events: auto;
      padding: 12px 20px;
      border-radius: 10px;
      background: rgba(18, 28, 45, 0.95);
      border: 1px solid var(--border-glow);
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
      backdrop-filter: var(--glass-blur);
      color: var(--text-main);
      font-size: 13px;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 10px;
      animation: slideIn 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .toast.error {
      border-color: rgba(244, 63, 94, 0.4);
      color: #fecdd3;
    }

    @keyframes slideIn {
      from { transform: translateX(100%); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }

    /* Lightbox Modal */
    .lightbox-modal {
      position: fixed;
      inset: 0;
      z-index: 3000;
      background: rgba(3, 5, 8, 0.92);
      backdrop-filter: blur(12px);
      display: none;
      place-items: center;
      padding: 30px;
    }

    .lightbox-modal.open {
      display: grid;
      animation: fadeIn 0.2s ease;
    }

    .lightbox-img {
      max-width: 90vw;
      max-height: 85vh;
      object-fit: contain;
      border-radius: 8px;
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.8);
    }

    .lightbox-close {
      position: absolute;
      top: 24px;
      right: 24px;
      width: 40px;
      height: 40px;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.1);
      border: 1px solid var(--border-subtle);
      color: #fff;
      font-size: 20px;
      cursor: pointer;
      display: grid;
      place-items: center;
    }

    .lightbox-close:hover {
      background: rgba(255, 255, 255, 0.2);
    }

    /* Responsive */
    @media (max-width: 1024px) {
      .grid-container { grid-template-columns: 1fr; }
      .metrics-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }

    @media (max-width: 640px) {
      .header-inner { flex-direction: column; align-items: flex-start; gap: 12px; }
      .metrics-grid { grid-template-columns: 1fr; }
      .workspace-tabs-bar { width: 100%; }
    }
  </style>
</head>
<body>

  <!-- Header -->
  <header class="app-header">
    <div class="header-inner">
      <a href="#" class="brand-logo">
        <div class="brand-icon-box">
          <svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
          </svg>
        </div>
        <div>
          <div style="display:flex; align-items:center; gap:8px;">
            <span class="brand-title">DocuVision</span>
            <span class="brand-tag">AI Vision v1.0</span>
          </div>
        </div>
      </a>

      <div class="status-badge">
        <span class="status-dot" id="statusDot"></span>
        <span id="statusText">System Ready</span>
      </div>

      <div class="header-actions">
        <button class="btn-quick-demo" id="btnDemoHeader">
          <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
          </svg>
          ⚡ Try Sample Preset
        </button>
        <span class="shortcut-pill">Press Ctrl + O</span>
      </div>
    </div>
  </header>

  <!-- Main Container -->
  <main class="main-wrapper">
    <div class="grid-container">
      
      <!-- Left Controls Panel -->
      <aside class="glass-panel">
        <div class="panel-header">
          <div class="panel-title">
            <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path>
            </svg>
            Media Upload Studio
          </div>
        </div>
        <div class="panel-body">
          <form id="uploadForm">
            <label class="dropzone-studio" id="dropzone">
              <input type="file" id="mediaInput" accept="image/*">
              <div class="upload-icon-ring">
                <svg width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 002-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                </svg>
              </div>
              <p class="drop-heading">Drop document photo here</p>
              <p class="drop-sub">or <span>browse computer</span> (JPG, PNG, WebP)</p>
            </label>

            <!-- Selected File Metadata -->
            <div class="file-preview-card" id="fileCard" style="display: none;">
              <div class="file-thumb-box" id="thumbBox">
                <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14"></path>
                </svg>
              </div>
              <div class="file-meta">
                <p class="file-name" id="fileName">document.jpg</p>
                <p class="file-size" id="fileSize">1.2 MB</p>
              </div>
            </div>

            <!-- Action Buttons -->
            <button type="submit" class="btn-scan-primary" id="btnScan" disabled>
              <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
              </svg>
              Run Document Scanner
            </button>

            <button type="button" class="btn-preset-panel" id="btnDemoPanel">
              <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
              </svg>
              Load Sample Document Preset
            </button>
          </form>

          <!-- Feature Highlights -->
          <div class="feature-list">
            <div class="feature-item">
              <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"></path>
              </svg>
              Auto Perspective Warp & Quad Alignment
            </div>
            <div class="feature-item">
              <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"></path>
              </svg>
              Adaptive Thresholding & Shadow Reduction
            </div>
            <div class="feature-item">
              <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"></path>
              </svg>
              Multi-metric Quality Scorecard (Blur & Skew)
            </div>
          </div>
        </div>
      </aside>

      <!-- Right Output Workspace -->
      <section>
        
        <!-- Workspace Tabs -->
        <nav class="workspace-tabs-bar">
          <button class="tab-btn active" data-tab="scannedTab">
            <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
            Scanned Document
          </button>
          <button class="tab-btn" data-tab="visualTab">
            <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
            </svg>
            Visual Pipeline Report
          </button>
          <button class="tab-btn" data-tab="qualityTab">
            <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
            </svg>
            Quality Metrics
          </button>
          <button class="tab-btn" data-tab="jsonTab">
            <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"></path>
            </svg>
            Raw JSON Report
          </button>
        </nav>

        <!-- Tab 1: Scanned Output -->
        <div class="tab-content active" id="scannedTab">
          <div class="result-display-card">
            <div class="display-preview-area" id="scannedPreview">
              <div class="empty-state-box">
                <div class="empty-icon">
                  <svg width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14"></path>
                  </svg>
                </div>
                <p style="font-weight: 700; font-size: 16px; margin-bottom: 4px; color: var(--text-main);">No Document Processed Yet</p>
                <p style="font-size: 13px;">Upload an image or try the sample preset to view the scanned result.</p>
              </div>
            </div>
            <div class="display-actions-bar">
              <button class="btn-action-outline" id="btnZoomScan" disabled>
                <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v6m3-3H7"></path>
                </svg>
                Inspect Fullscreen
              </button>
              <a class="btn-action-primary" id="btnDownloadScan" href="#" download aria-disabled="true">
                <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
                </svg>
                Download Scanned Image
              </a>
            </div>
          </div>
        </div>

        <!-- Tab 2: Visual Pipeline -->
        <div class="tab-content" id="visualTab">
          <div class="result-display-card">
            <div class="display-preview-area" id="visualPreview">
              <div class="empty-state-box">
                <div class="empty-icon">
                  <svg width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                  </svg>
                </div>
                <p style="font-weight: 700; font-size: 16px; margin-bottom: 4px; color: var(--text-main);">Pipeline Visual Report</p>
                <p style="font-size: 13px;">The computer vision processing breakdown will appear here.</p>
              </div>
            </div>
            <div class="display-actions-bar">
              <button class="btn-action-outline" id="btnZoomVisual" disabled>
                <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v6m3-3H7"></path>
                </svg>
                Inspect Fullscreen
              </button>
              <a class="btn-action-primary" id="btnDownloadReport" href="#" download aria-disabled="true">
                <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
                </svg>
                Download Visual Report
              </a>
            </div>
          </div>
        </div>

        <!-- Tab 3: Quality Analytics -->
        <div class="tab-content" id="qualityTab">
          <div class="quality-dashboard">
            <div class="verdict-banner" id="verdictBanner">
              <span class="verdict-badge pass" id="verdictBadge">READY</span>
              <p class="verdict-text" id="verdictText">Upload an image to evaluate image brightness, contrast, focus sharpness, and skew alignment.</p>
            </div>

            <div class="metrics-grid">
              <div class="metric-card">
                <div class="metric-top">
                  <span class="metric-label-text">Brightness</span>
                  <span class="metric-status-tag" id="tagBrightness">--</span>
                </div>
                <div class="metric-val-num" id="valBrightness">--</div>
                <div class="metric-progress-track">
                  <div class="metric-progress-fill" id="barBrightness"></div>
                </div>
              </div>

              <div class="metric-card">
                <div class="metric-top">
                  <span class="metric-label-text">Contrast</span>
                  <span class="metric-status-tag" id="tagContrast">--</span>
                </div>
                <div class="metric-val-num" id="valContrast">--</div>
                <div class="metric-progress-track">
                  <div class="metric-progress-fill" id="barContrast"></div>
                </div>
              </div>

              <div class="metric-card">
                <div class="metric-top">
                  <span class="metric-label-text">Sharpness</span>
                  <span class="metric-status-tag" id="tagSharpness">--</span>
                </div>
                <div class="metric-val-num" id="valSharpness">--</div>
                <div class="metric-progress-track">
                  <div class="metric-progress-fill" id="barSharpness"></div>
                </div>
              </div>

              <div class="metric-card">
                <div class="metric-top">
                  <span class="metric-label-text">Skew Angle</span>
                  <span class="metric-status-tag" id="tagSkew">--</span>
                </div>
                <div class="metric-val-num" id="valSkew">--</div>
                <div class="metric-progress-track">
                  <div class="metric-progress-fill" id="barSkew"></div>
                </div>
              </div>
            </div>

            <div style="display: flex; justify-content: flex-end;">
              <a class="btn-action-primary" id="btnDownloadJson" href="#" download aria-disabled="true">
                <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
                </svg>
                Download Quality JSON
              </a>
            </div>
          </div>
        </div>

        <!-- Tab 4: Raw JSON -->
        <div class="tab-content" id="jsonTab">
          <div class="result-display-card" style="padding: 20px;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px;">
              <span style="font-weight: 700; font-size: 14px; color: var(--text-muted);">Raw Quality Assessment Payload</span>
              <button class="btn-action-outline" id="btnCopyJson">
                <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                </svg>
                Copy to Clipboard
              </button>
            </div>
            <pre class="json-code-box" id="jsonCodeBox">// Scan payload will appear here after processing</pre>
          </div>
        </div>

      </section>
    </div>
  </main>

  <!-- Toast Container -->
  <div class="toast-container" id="toastContainer"></div>

  <!-- Lightbox Modal -->
  <div class="lightbox-modal" id="lightboxModal">
    <button class="lightbox-close" id="lightboxClose">&times;</button>
    <img src="" alt="Fullscreen View" class="lightbox-img" id="lightboxImg">
  </div>

  <script>
    // Elements
    const uploadForm = document.getElementById("uploadForm");
    const mediaInput = document.getElementById("mediaInput");
    const dropzone = document.getElementById("dropzone");
    const fileCard = document.getElementById("fileCard");
    const fileName = document.getElementById("fileName");
    const fileSize = document.getElementById("fileSize");
    const thumbBox = document.getElementById("thumbBox");
    const btnScan = document.getElementById("btnScan");
    const btnDemoHeader = document.getElementById("btnDemoHeader");
    const btnDemoPanel = document.getElementById("btnDemoPanel");
    const statusDot = document.getElementById("statusDot");
    const statusText = document.getElementById("statusText");
    const toastContainer = document.getElementById("toastContainer");

    // Previews & Downloads
    const scannedPreview = document.getElementById("scannedPreview");
    const visualPreview = document.getElementById("visualPreview");
    const btnDownloadScan = document.getElementById("btnDownloadScan");
    const btnDownloadReport = document.getElementById("btnDownloadReport");
    const btnDownloadJson = document.getElementById("btnDownloadJson");
    const btnZoomScan = document.getElementById("btnZoomScan");
    const btnZoomVisual = document.getElementById("btnZoomVisual");

    // Modal
    const lightboxModal = document.getElementById("lightboxModal");
    const lightboxImg = document.getElementById("lightboxImg");
    const lightboxClose = document.getElementById("lightboxClose");

    // Tabs
    const tabBtns = document.querySelectorAll(".tab-btn");
    const tabContents = document.querySelectorAll(".tab-content");

    let currentScanPayload = null;

    // Toast
    function showToast(message, isError = false) {
      const toast = document.createElement("div");
      toast.className = `toast ${isError ? "error" : ""}`;
      toast.innerHTML = `
        <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" viewBox="0 0 24 24">
          ${isError 
            ? '<path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>'
            : '<path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>'}
        </svg>
        <span>${message}</span>
      `;
      toastContainer.appendChild(toast);
      setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 250);
      }, 3500);
    }

    // Tab Switching
    tabBtns.forEach(btn => {
      btn.addEventListener("click", () => {
        const target = btn.dataset.tab;
        tabBtns.forEach(b => b.classList.remove("active"));
        tabContents.forEach(c => c.classList.remove("active"));
        btn.classList.add("active");
        document.getElementById(target).classList.add("active");
      });
    });

    // File Selection
    function handleFile(file) {
      if (!file) return;
      fileName.textContent = file.name;
      fileSize.textContent = `${(file.size / (1024 * 1024)).toFixed(2)} MB`;
      fileCard.style.display = "flex";
      btnScan.disabled = false;

      if (file.type.startsWith("image/")) {
        const reader = new FileReader();
        reader.onload = (e) => {
          thumbBox.innerHTML = `<img src="${e.target.result}" alt="Thumb">`;
        };
        reader.readAsDataURL(file);
      }
    }

    mediaInput.addEventListener("change", () => handleFile(mediaInput.files[0]));

    // Drag and Drop
    dropzone.addEventListener("dragover", (e) => {
      e.preventDefault();
      dropzone.classList.add("dragover");
    });
    dropzone.addEventListener("dragleave", () => dropzone.classList.remove("dragover"));
    dropzone.addEventListener("drop", (e) => {
      e.preventDefault();
      dropzone.classList.remove("dragover");
      if (e.dataTransfer.files.length) {
        mediaInput.files = e.dataTransfer.files;
        handleFile(e.dataTransfer.files[0]);
      }
    });

    // Status state
    function setStatus(busy, text) {
      statusText.textContent = text;
      statusDot.classList.toggle("busy", busy);
    }

    // Populate Results
    function renderResults(payload) {
      currentScanPayload = payload;

      // Scanned image
      const scanUrl = `${payload.scanned_document}?t=${Date.now()}`;
      scannedPreview.innerHTML = `<img src="${scanUrl}" alt="Scanned Document" id="scannedImg">`;
      btnDownloadScan.href = payload.scanned_document;
      btnDownloadScan.removeAttribute("aria-disabled");
      btnZoomScan.disabled = false;

      // Visual report
      const reportUrl = `${payload.visual_report}?t=${Date.now()}`;
      visualPreview.innerHTML = `<img src="${reportUrl}" alt="Visual Report" id="visualImg">`;
      btnDownloadReport.href = payload.visual_report;
      btnDownloadReport.removeAttribute("aria-disabled");
      btnZoomVisual.disabled = false;

      // Quality metrics
      const q = payload.quality;
      const banner = document.getElementById("verdictBanner");
      const badge = document.getElementById("verdictBadge");
      const text = document.getElementById("verdictText");

      if (q.passed) {
        banner.className = "verdict-banner";
        badge.className = "verdict-badge pass";
        badge.textContent = "PASS";
      } else {
        banner.className = "verdict-banner review";
        badge.className = "verdict-badge review";
        badge.textContent = "REVIEW REQUIRED";
      }
      text.textContent = q.messages ? q.messages.join(" ") : "Quality analysis completed.";

      // Metrics values
      document.getElementById("valBrightness").textContent = q.brightness ? q.brightness.toFixed(1) : "--";
      document.getElementById("valContrast").textContent = q.contrast ? q.contrast.toFixed(1) : "--";
      document.getElementById("valSharpness").textContent = q.sharpness ? q.sharpness.toFixed(1) : "--";
      document.getElementById("valSkew").textContent = q.skew_degrees !== undefined ? `${q.skew_degrees}°` : "--";

      document.getElementById("tagBrightness").textContent = (q.brightness >= 60 && q.brightness <= 220) ? "Good" : "Suboptimal";
      document.getElementById("tagBrightness").className = `metric-status-tag ${(q.brightness >= 60 && q.brightness <= 220) ? "ok" : ""}`;

      document.getElementById("tagContrast").textContent = q.contrast >= 25 ? "Good" : "Low";
      document.getElementById("tagContrast").className = `metric-status-tag ${q.contrast >= 25 ? "ok" : ""}`;

      document.getElementById("tagSharpness").textContent = q.sharpness >= 100 ? "Sharp" : "Blurry";
      document.getElementById("tagSharpness").className = `metric-status-tag ${q.sharpness >= 100 ? "ok" : ""}`;

      document.getElementById("tagSkew").textContent = Math.abs(q.skew_degrees) <= 5 ? "Aligned" : "Skewed";
      document.getElementById("tagSkew").className = `metric-status-tag ${Math.abs(q.skew_degrees) <= 5 ? "ok" : ""}`;

      // Progress bars
      document.getElementById("barBrightness").style.width = `${Math.min(100, (q.brightness / 255) * 100)}%`;
      document.getElementById("barContrast").style.width = `${Math.min(100, (q.contrast / 120) * 100)}%`;
      document.getElementById("barSharpness").style.width = `${Math.min(100, (q.sharpness / 2000) * 100)}%`;
      document.getElementById("barSkew").style.width = `${Math.min(100, (Math.abs(q.skew_degrees) / 15) * 100)}%`;

      btnDownloadJson.href = payload.quality_report;
      btnDownloadJson.removeAttribute("aria-disabled");

      // JSON Code Box
      document.getElementById("jsonCodeBox").textContent = JSON.stringify(q, null, 2);
    }

    // Submit Upload Form
    uploadForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const file = mediaInput.files[0];
      if (!file) return;

      const formData = new FormData();
      formData.append("media", file);

      btnScan.disabled = true;
      setStatus(true, "Processing Document...");
      showToast("Scanning & analyzing document...");

      try {
        const response = await fetch("/scan", { method: "POST", body: formData });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Processing failed.");

        renderResults(data);
        setStatus(false, "Analysis Complete");
        showToast("Document successfully processed!");
      } catch (err) {
        setStatus(false, "System Ready");
        showToast(err.message, true);
      } finally {
        btnScan.disabled = false;
      }
    });

    // Quick Demo Preset handler
    async function triggerDemoPreset() {
      setStatus(true, "Generating Sample Document...");
      showToast("Loading sample document demo...");

      try {
        const response = await fetch("/sample-demo");
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Demo failed.");

        renderResults(data);
        setStatus(false, "Analysis Complete");
        showToast("Sample document successfully analyzed!");
      } catch (err) {
        setStatus(false, "System Ready");
        showToast(err.message, true);
      }
    }

    btnDemoHeader.addEventListener("click", triggerDemoPreset);
    btnDemoPanel.addEventListener("click", triggerDemoPreset);

    // Lightbox Modal Zoom
    function openLightbox(src) {
      lightboxImg.src = src;
      lightboxModal.classList.add("open");
    }

    btnZoomScan.addEventListener("click", () => {
      const img = document.getElementById("scannedImg");
      if (img) openLightbox(img.src);
    });

    btnZoomVisual.addEventListener("click", () => {
      const img = document.getElementById("visualImg");
      if (img) openLightbox(img.src);
    });

    lightboxClose.addEventListener("click", () => lightboxModal.classList.remove("open"));
    lightboxModal.addEventListener("click", (e) => {
      if (e.target === lightboxModal) lightboxModal.classList.remove("open");
    });

    // Copy JSON
    document.getElementById("btnCopyJson").addEventListener("click", () => {
      const code = document.getElementById("jsonCodeBox").textContent;
      navigator.clipboard.writeText(code).then(() => {
        showToast("JSON copied to clipboard!");
      });
    });

    // Keyboard Shortcuts
    window.addEventListener("keydown", (e) => {
      if (e.ctrlKey && e.key.toLowerCase() === "o") {
        e.preventDefault();
        mediaInput.click();
      }
      if (e.key === "Escape" && lightboxModal.classList.contains("open")) {
        lightboxModal.classList.remove("open");
      }
    });
  </script>
</body>
</html>
"""


def _safe_output_path(url_path: str) -> Path | None:
    relative = unquote(url_path.removeprefix("/outputs/")).replace("/", os.sep)
    candidate = (OUTPUTS / relative).resolve()
    try:
        candidate.relative_to(OUTPUTS.resolve())
    except ValueError:
        return None
    return candidate


def _json(handler: BaseHTTPRequestHandler, status: HTTPStatus, payload: dict[str, object]) -> None:
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class DocuVisionHandler(BaseHTTPRequestHandler):
    server_version = "DocuVisionHTTP/1.0"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/":
            body = INDEX_HTML.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if parsed.path == "/sample-demo":
            self._handle_sample_demo()
            return

        if parsed.path.startswith("/outputs/"):
            self._serve_output(parsed.path)
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/scan":
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")
            return
        self._handle_scan()

    def _serve_output(self, path: str) -> None:
        file_path = _safe_output_path(path)
        if file_path is None or not file_path.exists() or not file_path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return

        content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
        data = file_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _handle_sample_demo(self) -> None:
        try:
            from scripts.generate_sample import create_sample

            sample_file = create_sample(ROOT / "samples" / "sample_document.jpg")
            run_id = "sample_" + uuid.uuid4().hex[:8]
            output_dir = UI_RUNS / run_id
            outputs = run(str(sample_file), str(output_dir))
            quality_path = outputs["quality_report"]
            quality = json.loads(Path(quality_path).read_text(encoding="utf-8"))

            def as_url(path: Path) -> str:
                return "/outputs/" + path.resolve().relative_to(OUTPUTS.resolve()).as_posix()

            _json(
                self,
                HTTPStatus.OK,
                {
                    "scanned_document": as_url(outputs["scanned_document"]),
                    "visual_report": as_url(outputs["visual_report"]),
                    "quality_report": as_url(outputs["quality_report"]),
                    "quality": quality,
                    "is_sample": True,
                },
            )
        except Exception as exc:
            _json(self, HTTPStatus.INTERNAL_SERVER_ERROR, {"error": f"Sample demo failed: {exc}"})

    def _handle_scan(self) -> None:
        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length <= 0 or content_length > MAX_UPLOAD_BYTES:
            _json(self, HTTPStatus.BAD_REQUEST, {"error": "Upload must be between 1 byte and 12 MB."})
            return

        body = self.rfile.read(content_length)
        content_type = self.headers.get("Content-Type", "")
        raw_headers = f"Content-Type: {content_type}\r\n\r\n".encode("utf-8")
        msg = BytesParser(policy=default).parsebytes(raw_headers + body)

        uploaded_file_name: str | None = None
        uploaded_file_data: bytes | None = None

        if msg.is_multipart():
            for part in msg.iter_parts():
                field_name = part.get_param("name", header="content-disposition")
                filename = part.get_filename()
                if field_name == "media" or filename:
                    uploaded_file_name = filename
                    uploaded_file_data = part.get_payload(decode=True)
                    break

        if uploaded_file_data is None or not uploaded_file_name:
            _json(self, HTTPStatus.BAD_REQUEST, {"error": "No image file was uploaded."})
            return

        extension = Path(uploaded_file_name).suffix.lower()
        if extension not in ALLOWED_EXTENSIONS:
            _json(self, HTTPStatus.BAD_REQUEST, {"error": "Unsupported image type."})
            return

        run_id = uuid.uuid4().hex[:12]
        UPLOADS.mkdir(parents=True, exist_ok=True)
        upload_path = UPLOADS / f"{run_id}{extension}"
        upload_path.write_bytes(uploaded_file_data)

        output_dir = UI_RUNS / run_id
        try:
            outputs = run(str(upload_path), str(output_dir))
            quality_path = outputs["quality_report"]
            quality = json.loads(Path(quality_path).read_text(encoding="utf-8"))
        except Exception as exc:
            _json(self, HTTPStatus.INTERNAL_SERVER_ERROR, {"error": f"Processing failed: {exc}"})
            return

        def as_url(path: Path) -> str:
            return "/outputs/" + path.resolve().relative_to(OUTPUTS.resolve()).as_posix()

        _json(
            self,
            HTTPStatus.OK,
            {
                "scanned_document": as_url(outputs["scanned_document"]),
                "visual_report": as_url(outputs["visual_report"]),
                "quality_report": as_url(outputs["quality_report"]),
                "quality": quality,
            },
        )

    def log_message(self, format: str, *args: object) -> None:
        sys.stdout.write("%s - %s\n" % (self.address_string(), format % args))


def serve(host: str = "127.0.0.1", port: int = 8000) -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer((host, port), DocuVisionHandler)
    print(f"DocuVision UI running at http://{host}:{port}")
    print("Press Ctrl+C to stop the server.")
    server.serve_forever()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Start the DocuVision browser upload UI.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8000, type=int)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    serve(args.host, args.port)


if __name__ == "__main__":
    main()
