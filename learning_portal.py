# -*- coding: utf-8 -*-
import http.server
import socketserver
import json
import webbrowser
import sys
import os
import tempfile
import subprocess
import urllib.parse
import threading
import time

PORT = 8000

# HTML, CSS, and JS combined into a single, self-contained template
HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Python Learning Portal</title>
  <!-- Premium Fonts -->
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-color: #0b0c10;
      --container-bg: rgba(31, 40, 51, 0.45);
      --border-color: rgba(255, 255, 255, 0.08);
      --accent-blue: #66fcf1;
      --accent-purple: #8e2de2;
      --accent-purple-light: #4a00e0;
      --text-main: #f5f5f7;
      --text-muted: #abb2bf;
      --console-bg: #1e1e24;
      --success-green: #39ff14;
      --error-red: #ff3333;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      /* Thin styled scrollbars for Firefox */
      scrollbar-width: thin;
      scrollbar-color: rgba(255, 255, 255, 0.12) rgba(11, 12, 16, 0.5);
    }

    /* Custom scrollbars for Chrome/Edge/Safari */
    ::-webkit-scrollbar {
      width: 6px;
      height: 6px;
    }

    ::-webkit-scrollbar-track {
      background: rgba(11, 12, 16, 0.3);
    }

    ::-webkit-scrollbar-thumb {
      background: rgba(255, 255, 255, 0.15);
      border-radius: 3px;
      transition: background 0.2s ease;
    }

    ::-webkit-scrollbar-thumb:hover {
      background: var(--accent-blue);
    }

    body {
      font-family: 'Outfit', sans-serif;
      background-color: var(--bg-color);
      background-image: 
        radial-gradient(at 10% 20%, rgba(142, 45, 226, 0.15) 0px, transparent 50%),
        radial-gradient(at 90% 80%, rgba(102, 252, 241, 0.15) 0px, transparent 50%);
      background-attachment: fixed;
      color: var(--text-main);
      height: 100vh;
      overflow: hidden;
      display: flex;
    }

    /* Sidebar Navigation */
    .sidebar {
      width: 280px;
      background: rgba(11, 12, 16, 0.85);
      border-right: 1px solid var(--border-color);
      display: flex;
      flex-direction: column;
      padding: 24px;
      z-index: 10;
    }

    .logo {
      font-weight: 800;
      font-size: 22px;
      background: linear-gradient(to right, var(--accent-blue), var(--accent-purple));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 32px;
      letter-spacing: 0.5px;
    }

    .module-list {
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 12px;
      flex-grow: 1;
      overflow-y: auto;
    }

    .module-item {
      padding: 14px 16px;
      border-radius: 12px;
      cursor: pointer;
      border: 1px solid transparent;
      transition: all 0.3s ease;
      background: rgba(255, 255, 255, 0.02);
    }

    .module-item:hover {
      background: rgba(255, 255, 255, 0.05);
      border-color: rgba(255, 255, 255, 0.1);
      transform: translateX(4px);
    }

    .module-item.active {
      background: linear-gradient(135deg, rgba(142, 45, 226, 0.2) 0%, rgba(102, 252, 241, 0.05) 100%);
      border-color: var(--accent-purple);
      box-shadow: 0 0 15px rgba(142, 45, 226, 0.2);
    }

    .module-title {
      font-weight: 600;
      font-size: 14px;
      margin-bottom: 4px;
    }

    .module-desc {
      font-size: 12px;
      color: var(--text-muted);
      line-height: 1.4;
    }

    /* Main Portal Grid */
    .main-content {
      flex-grow: 1;
      display: flex;
      flex-direction: column;
      height: 100vh;
    }

    .header-bar {
      height: 70px;
      border-bottom: 1px solid var(--border-color);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 32px;
      background: rgba(11, 12, 16, 0.5);
      backdrop-filter: blur(10px);
    }

    .active-module-header {
      font-weight: 600;
      font-size: 18px;
    }

    .grid-container {
      display: grid;
      grid-template-columns: 1.1fr 0.9fr;
      flex-grow: 1;
      overflow: hidden;
    }

    /* Left Side: Lesson text */
    .lesson-panel {
      border-right: 1px solid var(--border-color);
      padding: 32px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 20px;
      background: rgba(11, 12, 16, 0.2);
    }

    .lesson-panel h2 {
      font-size: 20px;
      font-weight: 600;
      margin-top: 10px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
      padding-bottom: 8px;
      color: var(--accent-blue);
    }

    .lesson-panel p {
      font-size: 15px;
      line-height: 1.6;
      color: var(--text-muted);
    }

    .lesson-panel ul {
      padding-left: 20px;
      color: var(--text-muted);
      font-size: 15px;
      line-height: 1.6;
    }

    .lesson-panel code {
      font-family: 'JetBrains Mono', monospace;
      background: rgba(255, 255, 255, 0.08);
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 14px;
      color: #ff79c6;
    }

    .lesson-panel pre {
      background: var(--console-bg);
      padding: 16px;
      border-radius: 12px;
      border: 1px solid var(--border-color);
      overflow-x: auto;
      margin: 12px 0;
    }

    .lesson-panel pre code {
      background: transparent;
      padding: 0;
      color: var(--text-main);
      font-size: 13px;
    }

    /* Right Side: Tabbed Code Playground */
    .playground-panel {
      display: flex;
      flex-direction: column;
      height: 100%;
      overflow: hidden;
    }

    .tabs-header {
      display: flex;
      background: rgba(11, 12, 16, 0.4);
      border-bottom: 1px solid var(--border-color);
      overflow-x: auto;
    }

    .tab-btn {
      padding: 16px 24px;
      background: transparent;
      border: none;
      color: var(--text-muted);
      font-family: inherit;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
      border-bottom: 2px solid transparent;
      white-space: nowrap;
    }

    .tab-btn:hover {
      color: var(--text-main);
      background: rgba(255, 255, 255, 0.02);
    }

    .tab-btn.active {
      color: var(--accent-blue);
      border-bottom-color: var(--accent-blue);
      background: rgba(255, 255, 255, 0.04);
    }

    /* Lab Instructions inside Playground */
    .lab-instructions {
      padding: 20px 24px;
      background: rgba(142, 45, 226, 0.06);
      border-bottom: 1px solid var(--border-color);
      font-size: 14px;
      line-height: 1.5;
      color: var(--text-main);
    }

    /* Editor Area */
    .editor-container {
      flex-grow: 1;
      position: relative;
      background: rgba(30, 30, 36, 0.3);
      display: flex;
      flex-direction: column;
      min-height: 0;
    }

    .editor-wrapper {
      display: flex;
      flex-grow: 1;
      position: relative;
      overflow: hidden;
      height: 100%;
      min-height: 0;
    }

    .line-numbers {
      min-width: 48px;
      width: auto;
      text-align: right;
      padding: 24px 12px 24px 12px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 14px;
      line-height: 1.6;
      color: rgba(255, 255, 255, 0.25);
      border-right: 1px solid var(--border-color);
      background: rgba(11, 12, 16, 0.15);
      user-select: none;
      overflow-y: hidden;
      box-sizing: border-box;
      white-space: pre;
    }

    .editor-textarea {
      flex-grow: 1;
      background: transparent;
      border: none;
      color: #f8f8f2;
      font-family: 'JetBrains Mono', monospace;
      font-size: 14px;
      line-height: 1.6;
      padding: 24px 24px 24px 16px;
      resize: none;
      outline: none;
      tab-size: 4;
      overflow: auto;
      white-space: pre;
      box-sizing: border-box;
    }

    /* Console Area */
    .console-container {
      height: 200px;
      background: var(--console-bg);
      border-top: 1px solid var(--border-color);
      display: flex;
      flex-direction: column;
    }

    .console-header {
      padding: 8px 24px;
      background: rgba(0, 0, 0, 0.2);
      font-size: 12px;
      font-weight: 600;
      color: var(--text-muted);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .console-output {
      flex-grow: 1;
      padding: 16px 24px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 13px;
      overflow-y: auto;
      color: #50fa7b;
      white-space: pre-wrap;
    }

    /* Action Buttons */
    .controls-row {
      padding: 16px 24px;
      display: flex;
      gap: 16px;
      background: rgba(11, 12, 16, 0.8);
      border-top: 1px solid var(--border-color);
      justify-content: flex-end;
    }

    .btn {
      padding: 10px 24px;
      border-radius: 8px;
      font-family: inherit;
      font-weight: 600;
      font-size: 14px;
      cursor: pointer;
      transition: all 0.2s ease;
      border: 1px solid transparent;
    }

    .btn-run {
      background: transparent;
      color: var(--text-main);
      border-color: rgba(255, 255, 255, 0.2);
    }

    .btn-run:hover {
      background: rgba(255, 255, 255, 0.05);
      border-color: var(--accent-blue);
      color: var(--accent-blue);
    }

    .btn-test {
      background: linear-gradient(135deg, var(--accent-purple) 0%, var(--accent-purple-light) 100%);
      color: white;
      box-shadow: 0 4px 15px rgba(142, 45, 226, 0.4);
    }

    .btn-test:hover {
      transform: translateY(-1px);
      box-shadow: 0 6px 20px rgba(142, 45, 226, 0.6);
    }

    /* Confetti canvas */
    #confetti-canvas {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      z-index: 99;
    }

    /* Success screen overlay */
    .success-overlay {
      display: none;
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(11, 12, 16, 0.95);
      z-index: 50;
      justify-content: center;
      align-items: center;
      flex-direction: column;
      gap: 16px;
      animation: pop 0.3s ease forwards;
    }

    .success-overlay h3 {
      font-size: 28px;
      font-weight: 800;
      color: var(--success-green);
    }

    .success-overlay p {
      color: var(--text-muted);
      font-size: 16px;
      margin-bottom: 12px;
    }

    /* Interactive navigation elements */
    .step-navigation {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: auto;
      padding-top: 20px;
      border-top: 1px solid var(--border-color);
    }

    .demo-box {
      background: rgba(102, 252, 241, 0.05);
      border: 1px dashed var(--accent-blue);
      border-radius: 12px;
      padding: 20px;
      margin-top: 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .demo-box h4 {
      font-size: 14px;
      font-weight: 600;
      color: var(--accent-blue);
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .demo-box pre {
      background: var(--console-bg);
      border-radius: 8px;
      border: 1px solid var(--border-color);
      margin: 0;
    }

    .btn-demo-load {
      background: transparent;
      color: var(--accent-blue);
      border-color: var(--accent-blue);
      width: 100%;
      text-align: center;
      font-size: 13px;
      padding: 8px 12px;
    }

    .btn-demo-load:hover {
      background: rgba(102, 252, 241, 0.1);
    }

    @keyframes pop {
      0% { transform: scale(0.9); opacity: 0; }
      100% { transform: scale(1); opacity: 1; }
    }
  </style>
</head>
<body>
  <canvas id="confetti-canvas"></canvas>

  <!-- Sidebar Module Navigation -->
  <div class="sidebar">
    <div class="logo">Python Studio</div>
    <ul class="module-list" id="module-list-container">
      <!-- Populated via Javascript -->
    </ul>
  </div>

  <!-- Main Workspace -->
  <div class="main-content">
    <div class="header-bar">
      <div class="active-module-header" id="active-module-title">Loading module...</div>
    </div>

    <div class="grid-container">
      <!-- Left Side: Interactive Step Explanations -->
      <div class="lesson-panel" id="lesson-content-container">
        <!-- Dynamically populated per slide step -->
      </div>

      <!-- Right Side: Coding Sandbox -->
      <div class="playground-panel">
        <div class="tabs-header" id="tabs-container">
          <!-- Populated via Javascript -->
        </div>

        <div class="lab-instructions" id="lab-instructions-container" style="display: none;">
          <!-- Populated via Javascript -->
        </div>

        <div class="editor-container">
          <div class="editor-wrapper">
            <div class="line-numbers" id="line-numbers">1</div>
            <textarea class="editor-textarea" id="editor" spellcheck="false"></textarea>
          </div>

          <div class="success-overlay" id="success-overlay">
            <h3>Lab Passed!</h3>
            <p>You solved this exercise successfully.</p>
            <button class="btn btn-test" onclick="dismissSuccess()">Keep Coding</button>
          </div>
        </div>

        <div class="console-container">
          <div class="console-header">
            <span>CONSOLE OUTPUT</span>
            <span id="console-status" style="color: var(--accent-blue)">idle</span>
          </div>
          <div class="console-output" id="console-output">Ready to execute code...</div>
        </div>

        <div class="controls-row">
          <button class="btn btn-run" id="btn-run" onclick="runCode()">Run Code</button>
          <button class="btn btn-test" id="btn-test" onclick="testCode()" style="display: none;">Submit & Check</button>
        </div>
      </div>
    </div>
  </div>

  <script>
    let courseData = null;
    let currentModuleIndex = 0;
    let currentTabId = "lesson"; // "lesson" or "lab_0", "lab_1", etc.
    let currentStepIndex = 0; // Tracks slide index inside active module
    let codeCache = {}; // Stores user code draft for each tab so switching tabs doesn't lose work
    let completedSteps = {}; // Tracks step completion status: "module_step" -> true
    let currentLabMode = {}; // "moduleId_tabId" -> "normal" or "variant"
    let usedHelpForCurrentLab = {}; // "moduleId_tabId_mode" -> true or false

    // Load Course Data from Server
    async function fetchCourseData() {
      try {
        const res = await fetch("/api/data");
        courseData = await res.json();
        
        try {
          const progRes = await fetch("/api/load_progress");
          const progress = await progRes.json();
          
          currentModuleIndex = progress.currentModuleIndex !== undefined ? progress.currentModuleIndex : 0;
          currentStepIndex = progress.currentStepIndex !== undefined ? progress.currentStepIndex : 0;
          currentTabId = progress.currentTabId !== undefined ? progress.currentTabId : "lesson";
          codeCache = progress.codeCache || {};
          completedSteps = progress.completedSteps || {};
          currentLabMode = progress.currentLabMode || {};
          usedHelpForCurrentLab = progress.usedHelpForCurrentLab || {};
        } catch (progErr) {
          loadProgress();
        }
        
        renderSidebar();
        loadModule(currentModuleIndex, true);
        selectTab(currentTabId, true);
      } catch (err) {
        console.error("Failed to fetch course data:", err);
        document.getElementById("console-output").innerText = "Error: Failed to connect to server backend.";
      }
    }

    async function saveProgress() {
      try {
        localStorage.setItem("currentModuleIndex", currentModuleIndex);
        localStorage.setItem("currentStepIndex", currentStepIndex);
        localStorage.setItem("currentTabId", currentTabId);
        localStorage.setItem("codeCache", JSON.stringify(codeCache));
        localStorage.setItem("completedSteps", JSON.stringify(completedSteps));
        localStorage.setItem("currentLabMode", JSON.stringify(currentLabMode));
        localStorage.setItem("usedHelpForCurrentLab", JSON.stringify(usedHelpForCurrentLab));
        
        await fetch("/api/save_progress", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            currentModuleIndex,
            currentStepIndex,
            currentTabId,
            codeCache,
            completedSteps,
            currentLabMode,
            usedHelpForCurrentLab
          })
        });
      } catch (e) {
        console.error("Failed to save progress:", e);
      }
    }

    // Restore user state
    function loadProgress() {
      try {
        const savedMod = localStorage.getItem("currentModuleIndex");
        if (savedMod !== null) currentModuleIndex = parseInt(savedMod);

        const savedStep = localStorage.getItem("currentStepIndex");
        if (savedStep !== null) currentStepIndex = parseInt(savedStep);

        const savedTab = localStorage.getItem("currentTabId");
        if (savedTab !== null) currentTabId = savedTab;

        const savedCache = localStorage.getItem("codeCache");
        if (savedCache !== null) codeCache = JSON.parse(savedCache);

        const savedCompleted = localStorage.getItem("completedSteps");
        if (savedCompleted !== null) completedSteps = JSON.parse(savedCompleted);
        
        const savedLabMode = localStorage.getItem("currentLabMode");
        if (savedLabMode !== null) currentLabMode = JSON.parse(savedLabMode);
        else currentLabMode = {};

        const savedUsedHelp = localStorage.getItem("usedHelpForCurrentLab");
        if (savedUsedHelp !== null) usedHelpForCurrentLab = JSON.parse(savedUsedHelp);
        else usedHelpForCurrentLab = {};
      } catch (e) {
        console.error("Failed to load progress:", e);
      }
    }

    // Render Sidebar Menu
    function renderSidebar() {
      const container = document.getElementById("module-list-container");
      container.innerHTML = "";
      courseData.modules.forEach((mod, idx) => {
        const li = document.createElement("li");
        li.className = `module-item ${idx === currentModuleIndex ? 'active' : ''}`;
        li.onclick = () => loadModule(idx);
        li.innerHTML = `
          <div class="module-title">${mod.title}</div>
          <div class="module-desc">${mod.description}</div>
        `;
        container.appendChild(li);
      });
    }

    // Load specific course module
    function loadModule(idx, isStartup = false) {
      currentModuleIndex = idx;
      if (!isStartup) {
        currentStepIndex = 0; // Reset slide step
        currentTabId = "lesson"; // Reset tab
      }
      
      const items = document.querySelectorAll(".module-item");
      items.forEach((item, itemIdx) => {
        if (itemIdx === idx) item.classList.add("active");
        else item.classList.remove("active");
      });

      const mod = courseData.modules[idx];
      document.getElementById("active-module-title").innerText = mod.title;

      // Render Tabs Header
      const tabsContainer = document.getElementById("tabs-container");
      tabsContainer.innerHTML = "";

      // Always add Lesson tab
      const lessonTab = document.createElement("button");
      lessonTab.className = "tab-btn active";
      lessonTab.innerText = "Lesson Guide";
      lessonTab.onclick = () => selectTab("lesson");
      lessonTab.id = "tab-btn-lesson";
      tabsContainer.appendChild(lessonTab);

      // Add Lab tabs
      mod.labs.forEach((lab, labIdx) => {
        const labTab = document.createElement("button");
        labTab.className = "tab-btn";
        labTab.innerText = `Lab: ${lab.title}`;
        labTab.onclick = () => selectTab(`lab_${labIdx}`);
        labTab.id = `tab-btn-lab_${labIdx}`;
        tabsContainer.appendChild(labTab);
      });

      if (!isStartup) {
        selectTab("lesson");
      }
      saveProgress();
    }

    // Select active playground tab
    function selectTab(tabId, isStartup = false) {
      // Save current code to cache before switching (skip during startup)
      if (!isStartup) {
        if (currentTabId !== "lesson") {
          const modeKey = `${currentModuleIndex}_${currentTabId}`;
          const currentMode = currentLabMode[modeKey] || "normal";
          codeCache[`${currentModuleIndex}_${currentTabId}_${currentMode}`] = document.getElementById("editor").value;
        } else {
          codeCache[`${currentModuleIndex}_lesson_step_${currentStepIndex}`] = document.getElementById("editor").value;
        }
      }

      currentTabId = tabId;

      // Update Tab Buttons UI
      const btns = document.querySelectorAll(".tab-btn");
      btns.forEach(btn => {
        if (btn.id === `tab-btn-${tabId}`) btn.classList.add("active");
        else btn.classList.remove("active");
      });

      const mod = courseData.modules[currentModuleIndex];
      const instructionsContainer = document.getElementById("lab-instructions-container");
      const testBtn = document.getElementById("btn-test");

      if (tabId === "lesson") {
        instructionsContainer.style.display = "none";
        testBtn.style.display = "none";
        renderActiveStep();
      } else {
        // Lab tab selected
        const labIdx = parseInt(tabId.split("_")[1]);
        const lab = mod.labs[labIdx];
        const modeKey = `${currentModuleIndex}_${tabId}`;
        const currentMode = currentLabMode[modeKey] || "normal";
        
        let instructions = lab.instructions;
        let initialCode = lab.initial_code;
        let exampleCode = lab.example_code;
        let helpText = lab.help_text;
        
        if (currentMode === "variant") {
          instructions = lab.instructions_variant || lab.instructions;
          initialCode = lab.initial_code_variant !== undefined ? lab.initial_code_variant : lab.initial_code;
          exampleCode = lab.example_code_variant || lab.example_code;
          helpText = lab.help_text_variant || lab.help_text;
        }

        let exampleHtml = "";
        if (exampleCode) {
          exampleHtml = `
            <div class="demo-box" style="margin-top: 24px; border-color: rgba(255, 255, 255, 0.15); background: rgba(255, 255, 255, 0.02);">
              <h4 style="color: var(--text-main);">Example Pattern</h4>
              <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 8px;">Here is an example of the pattern you need, using different names and values:</p>
              <pre style="margin: 0;"><code style="font-size: 12px; color: #abb2bf;">${exampleCode}</code></pre>
            </div>
          `;
        }

        const helpStateKey = `${modeKey}_${currentMode}`;
        const hasUsedHelp = usedHelpForCurrentLab[helpStateKey] || false;
        
        const helpBtnHtml = hasUsedHelp ? "" : `
          <button class="btn btn-demo-load" id="btn-help" onclick="toggleHelp()" style="margin-top: 16px; border-color: #ffb86c; color: #ffb86c; font-size: 13px; width: 100%; text-align: center;">Need More Help?</button>
        `;
        
        const helpBoxStyle = hasUsedHelp ? "block" : "none";
        const helpBoxHtml = `
          <div id="help-box" style="display: ${helpBoxStyle}; margin-top: 16px; border: 1px solid #ffb86c; background: rgba(255, 184, 108, 0.05); padding: 16px; border-radius: 12px;">
            <strong style="color: #ffb86c; font-size: 14px;">Step-by-Step Help:</strong>
            <pre style="margin-top: 8px; background: var(--console-bg); border-radius: 8px; border: 1px solid var(--border-color); padding: 12px; overflow-x: auto;"><code style="font-size: 12px; color: #ffb86c;">${helpText}</code></pre>
            <p style="font-size: 12px; color: var(--text-muted); margin-top: 8px; line-height: 1.4;">Note: Since you activated Help, you will need to complete a variant challenge without Help to pass this lab!</p>
          </div>
        `;

        document.getElementById("lesson-content-container").innerHTML = `
          <h2>${lab.title} ${currentMode === "variant" ? "[Variant]" : ""}</h2>
          <p style="margin-top: 12px; line-height: 1.6; color: var(--text-muted);">${instructions}</p>
          ${exampleHtml}
          ${helpBtnHtml}
          ${helpBoxHtml}
          <hr style="border: none; border-top: 1px solid var(--border-color); margin: 24px 0;">
          <h3 style="color: var(--text-main); font-size: 16px;">Self-Checking Lab</h3>
          <p style="margin-top: 8px; line-height: 1.6; color: var(--text-muted);">Type your code in the sandbox on the right. Once you think it's ready, click the glowing <b>Submit & Check</b> button below to let the server check your answer!</p>
        `;

        instructionsContainer.innerHTML = `<strong>Challenge:</strong> ${instructions}`;
        instructionsContainer.style.display = "block";
        testBtn.style.display = "block";

        // Load initial code or user's cached draft
        const cacheKey = `${currentModuleIndex}_${tabId}_${currentMode}`;
        document.getElementById("editor").value = codeCache[cacheKey] !== undefined ? codeCache[cacheKey] : initialCode;
      }

      document.getElementById("console-output").innerText = "Ready to run code...";
      document.getElementById("console-status").innerText = "idle";
      document.getElementById("console-status").style.color = "var(--accent-blue)";
      saveProgress();
      updateLineNumbers();
      syncScroll();
    }

    // Render current interactive step details
    function renderActiveStep() {
      const mod = courseData.modules[currentModuleIndex];
      const step = mod.steps[currentStepIndex];
      const container = document.getElementById("lesson-content-container");

      // Format demo HTML block
      let demoBoxHtml = "";
      if (step.demo_code) {
        demoBoxHtml = `
          <div class="demo-box">
            <h4> Demonstration Example</h4>
            <pre><code>${step.demo_code}</code></pre>
            <button class="btn btn-demo-load" onclick="loadDemoCode()"> Load Demo Code into Editor</button>
          </div>
        `;
      }

      const stepKey = `${currentModuleIndex}_${currentStepIndex}`;
      const isStepDone = completedSteps[stepKey] || false;
      let nextBtnHtml = "";
      if (!isStepDone) {
        nextBtnHtml = `<button class="btn" id="btn-next" disabled style="opacity: 0.3; cursor: not-allowed; background: rgba(255,255,255,0.05); border-color: rgba(255,255,255,0.1); color: var(--text-muted); box-shadow: none;">Run Code to Unlock</button>`;
      } else {
        nextBtnHtml = `<button class="btn btn-test" id="btn-next" onclick="nextStep()">${currentStepIndex === mod.steps.length - 1 ? 'Go to Lab' : 'Next'}</button>`;
      }

      container.innerHTML = `
        <h2>${step.title}</h2>
        <div style="margin-top: 12px; color: var(--text-muted);">${step.concept}</div>
        ${demoBoxHtml}
        <div style="margin-top: 16px; background: rgba(255,255,255,0.01); border: 1px solid var(--border-color); padding: 16px; border-radius: 12px;">
          <strong style="color: var(--accent-blue); font-size: 14px;">Your Turn:</strong>
          <p style="margin-top: 4px; font-size: 14px; color: var(--text-main);">${step.instructions}</p>
        </div>
        <div class="step-navigation">
          <button class="btn btn-run" id="btn-prev" onclick="prevStep()" ${currentStepIndex === 0 ? 'disabled style="opacity: 0.3; cursor: not-allowed;"' : ''}>Back</button>
          <span style="font-size: 13px; font-weight: 600; color: var(--text-muted);">Step ${currentStepIndex + 1} of ${mod.steps.length}</span>
          ${nextBtnHtml}
        </div>
      `;

      // Load saved editor cache or sample code
      const stepCodeKey = `${currentModuleIndex}_lesson_step_${currentStepIndex}`;
      document.getElementById("editor").value = codeCache[stepCodeKey] !== undefined ? codeCache[stepCodeKey] : (step.demo_code || "");
      saveProgress();
      updateLineNumbers();
      syncScroll();
    }

    function loadDemoCode() {
      const mod = courseData.modules[currentModuleIndex];
      const step = mod.steps[currentStepIndex];
      if (step.demo_code) {
        document.getElementById("editor").value = step.demo_code;
        const stepCodeKey = `${currentModuleIndex}_lesson_step_${currentStepIndex}`;
        codeCache[stepCodeKey] = step.demo_code;
        document.getElementById("console-output").innerText = "Demo code loaded! Click 'Run Code' to see it execute.";
        saveProgress();
        updateLineNumbers();
        syncScroll();
      }
    }

    function nextStep() {
      const mod = courseData.modules[currentModuleIndex];
      // Save current code draft first
      codeCache[`${currentModuleIndex}_lesson_step_${currentStepIndex}`] = document.getElementById("editor").value;

      if (currentStepIndex < mod.steps.length - 1) {
        currentStepIndex++;
        renderActiveStep();
      } else {
        // If last step, jump directly to first lab
        selectTab("lab_0");
      }
      saveProgress();
    }

    function prevStep() {
      if (currentStepIndex > 0) {
        codeCache[`${currentModuleIndex}_lesson_step_${currentStepIndex}`] = document.getElementById("editor").value;
        currentStepIndex--;
        renderActiveStep();
      }
      saveProgress();
    }

    // Run Code in Background or Interactive Mode
    async function runCode() {
      const code = document.getElementById("editor").value;
      const statusLabel = document.getElementById("console-status");
      const outputArea = document.getElementById("console-output");

      statusLabel.innerText = "running...";
      statusLabel.style.color = "yellow";
      outputArea.innerText = "Executing your code on local server...";

      try {
        const res = await fetch("/api/run", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ code })
        });
        const result = await res.json();
        
        if (result.interactive) {
          outputArea.innerText = result.stdout;
          statusLabel.innerText = "interactive";
          statusLabel.style.color = "var(--success-green)";
          
          // Unlock next slide when running interactive code
          if (currentTabId === "lesson") {
            const stepKey = `${currentModuleIndex}_${currentStepIndex}`;
            completedSteps[stepKey] = true;
            renderActiveStep();
          }
        } else {
          if (result.stderr) {
            const tip = generateFriendlyTip(result.stderr);
            if (tip) {
              outputArea.innerText = `Code Run Error!

${tip}

--------------------------------------------------
[Technical Details]
${result.stderr}`;
            } else {
              outputArea.innerText = result.stderr;
            }
            outputArea.style.color = "var(--error-red)";
            statusLabel.innerText = "error";
            statusLabel.style.color = "var(--error-red)";
          } else {
            outputArea.innerText = result.stdout || "[Code executed successfully with no print output]";
            outputArea.style.color = "#50fa7b";
            statusLabel.innerText = "success";
            statusLabel.style.color = "var(--success-green)";
            
            // Unlock next slide upon successful background run
            if (currentTabId === "lesson") {
              const stepKey = `${currentModuleIndex}_${currentStepIndex}`;
              completedSteps[stepKey] = true;
              renderActiveStep();
            }
          }
        }
      } catch (err) {
        outputArea.innerText = "Error contacting backend server.";
        outputArea.style.color = "var(--error-red)";
        statusLabel.innerText = "failed";
        statusLabel.style.color = "var(--error-red)";
      }
    }

    // Submit & Check Code against Test Suite
    async function testCode() {
      if (currentTabId === "lesson") return;
      const code = document.getElementById("editor").value;
      const labIdx = parseInt(currentTabId.split("_")[1]);
      const lab = courseData.modules[currentModuleIndex].labs[labIdx];

      const modeKey = `${currentModuleIndex}_${currentTabId}`;
      const currentMode = currentLabMode[modeKey] || "normal";
      let test_code = lab.test_code;
      if (currentMode === "variant") {
        test_code = lab.test_code_variant || lab.test_code;
      }

      const statusLabel = document.getElementById("console-status");
      const outputArea = document.getElementById("console-output");

      statusLabel.innerText = "verifying...";
      statusLabel.style.color = "yellow";
      outputArea.innerText = "Running verification tests...";

      try {
        const res = await fetch("/api/test", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ code, test_code })
        });
        const result = await res.json();

        if (result.passed) {
          outputArea.innerText = result.stdout + "\\nVerification Successful! All tests passed.";
          outputArea.style.color = "var(--success-green)";
          statusLabel.innerText = "passed";
          statusLabel.style.color = "var(--success-green)";
          
          const helpStateKey = `${modeKey}_${currentMode}`;
          const usedHelp = usedHelpForCurrentLab[helpStateKey] || false;
          
          if (usedHelp) {
            setTimeout(() => {
              if (currentMode === "normal") {
                alert("Normal exercise completed with Help! To complete this lab, you must now solve a variant exercise WITHOUT using Help. We've updated your instructions and code templates!");
                currentLabMode[modeKey] = "variant";
                const variantHelpKey = `${modeKey}_variant`;
                usedHelpForCurrentLab[variantHelpKey] = false;
              } else {
                alert("Variant completed with Help! You must complete this exercise WITHOUT using Help. Toggling back to the original exercise so you can try on your own!");
                currentLabMode[modeKey] = "normal";
                const normalHelpKey = `${modeKey}_normal`;
                usedHelpForCurrentLab[normalHelpKey] = false;
              }
              selectTab(currentTabId);
            }, 500);
          } else {
            // Show success screen and trigger confetti
            document.getElementById("success-overlay").style.display = "flex";
            triggerConfetti();
          }
        } else {
          let errMsg = result.stderr || "One or more verification tests failed. Double check your variable names, values, or logic!";
          const tip = generateFriendlyTip(result.stderr);
          const stdoutPrefix = result.stdout ? result.stdout + "\\n" : "";
          if (tip) {
            outputArea.innerText = `${stdoutPrefix}Verification Failed!\\n\\n${tip}\\n\\n--------------------------------------------------\\n[Technical Details]\\n${errMsg}`;
          } else {
            outputArea.innerText = `${stdoutPrefix}Verification Failed!\\n\\n${errMsg}`;
          }
          outputArea.style.color = "var(--error-red)";
          statusLabel.innerText = "failed";
          statusLabel.style.color = "var(--error-red)";
        }
      } catch (err) {
        outputArea.innerText = "Error contacting backend server.";
        outputArea.style.color = "var(--error-red)";
        statusLabel.innerText = "failed";
      }
    }

    function dismissSuccess() {
      document.getElementById("success-overlay").style.display = "none";
      
      // Auto-advance to the next lab or module
      if (currentTabId.startsWith("lab_")) {
        const labIdx = parseInt(currentTabId.split("_")[1]);
        const mod = courseData.modules[currentModuleIndex];
        
        if (labIdx < mod.labs.length - 1) {
          // Go to the next lab exercise
          selectTab(`lab_${labIdx + 1}`);
        } else {
          // All labs in this module completed
          if (currentModuleIndex < courseData.modules.length - 1) {
            alert(`Module completed! Moving to the next module: ${courseData.modules[currentModuleIndex + 1].title}`);
            loadModule(currentModuleIndex + 1);
          } else {
            // All modules completed
            alert("CONGRATULATIONS! You have completed the final project and finished the entire Python course! Keep practicing and happy coding!");
          }
        }
      }
    }

    function toggleHelp() {
      const helpBox = document.getElementById("help-box");
      if (!helpBox) return;
      
      const modeKey = `${currentModuleIndex}_${currentTabId}`;
      const currentMode = currentLabMode[modeKey] || "normal";
      const helpStateKey = `${modeKey}_${currentMode}`;
      
      usedHelpForCurrentLab[helpStateKey] = true;
      helpBox.style.display = "block";
      
      const helpBtn = document.getElementById("btn-help");
      if (helpBtn) helpBtn.style.display = "none";
      
      saveProgress();
    }

    function generateFriendlyTip(stderr) {
      if (!stderr) return "";
      
      // Parse AssertionError
      if (stderr.includes("AssertionError:")) {
        const match = stderr.match(/AssertionError:\\s*(.*)/);
        if (match && match[1]) {
          const assertMsg = match[1].trim();
          return `Quick Tip:\n${assertMsg}\n\nDouble check your code to make sure you named your variables correctly, used the exact values requested (watch out for lowercase/uppercase!), and followed the instructions closely.`;
        }
      }
      
      // Parse IndentationError
      if (stderr.includes("IndentationError:")) {
        const lineMatch = stderr.match(/line\\s+(\\d+)/i);
        const lineStr = lineMatch ? `on line ${lineMatch[1]}` : "";
        return `Quick Tip:\nThere is an Indentation Error ${lineStr}!\n\nPython requires you to align your code blocks. If you are writing code inside an 'if' statement, 'else' block, 'for' loop, or 'while' loop, make sure the lines inside that block start with exactly 4 spaces.`;
      }

      // Parse SyntaxError
      if (stderr.includes("SyntaxError:")) {
        const lineMatch = stderr.match(/line\\s+(\\d+)/i);
        const lineStr = lineMatch ? `on line ${lineMatch[1]}` : "";
        const descMatch = stderr.match(/SyntaxError:\\s*(.*)/);
        const desc = descMatch ? descMatch[1].trim() : "invalid syntax";
        return `Quick Tip:\nThere is a Syntax Error (typo) ${lineStr}: "${desc}"!\n\nThis means Python ran into a spelling or grammar rule it didn't understand. Check if you forgot a colon (:), mismatched parentheses (), or left a quote open.`;
      }

      // Parse NameError
      if (stderr.includes("NameError:")) {
        const match = stderr.match(/NameError:\\s*(.*)/);
        const desc = match ? match[1].trim() : "";
        return `Quick Tip:\nPython ran into a Name Error!\n\n${desc}\n\nThis usually means you are using a variable name or function name that you haven't created yet, or it's misspelled. Make sure you spelled it exactly the same way everywhere.`;
      }

      // Parse TypeError
      if (stderr.includes("TypeError:")) {
        const match = stderr.match(/TypeError:\\s*(.*)/);
        const desc = match ? match[1].trim() : "";
        return `Quick Tip:\nThere is a Type Error!\n\n${desc}\n\nThis happens when you try to mix incompatible types (like adding text strings and numbers together). You might need to convert numbers to strings using str(), or vice-versa using int().`;
      }

      // Parse KeyError
      if (stderr.includes("KeyError:")) {
        const match = stderr.match(/KeyError:\\s*(.*)/);
        const desc = match ? match[1].trim() : "";
        return `Quick Tip:\nThere is a Key Error!\n\nPython couldn't find the key ${desc} in your dictionary. Check if the key exists or if there is a spelling typo.`;
      }

      // Parse IndexError
      if (stderr.includes("IndexError:")) {
        return `Quick Tip:\nThere is an Index Error!\n\nYou are trying to access a list item at an index that doesn't exist (it is out of range). Remember that list indexing starts at 0, so a list with 3 items only goes up to index 2.`;
      }
      
      return "";
    }

    // Confetti Canvas Particle System
    function triggerConfetti() {
      const canvas = document.getElementById('confetti-canvas');
      const ctx = canvas.getContext('2d');
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      
      let particles = [];
      for (let i = 0; i < 150; i++) {
        particles.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height - canvas.height,
          r: Math.random() * 6 + 4,
          d: Math.random() * canvas.height,
          color: `hsl(${Math.random() * 360}, 100%, 50%)`,
          tilt: Math.random() * 10 - 5,
          tiltAngleIncremental: Math.random() * 0.07 + 0.02,
          tiltAngle: 0
        });
      }
      
      function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        particles.forEach((p, idx) => {
          p.tiltAngle += p.tiltAngleIncremental;
          p.y += (Math.cos(p.d) + 3 + p.r / 2) / 2;
          p.x += Math.sin(p.tiltAngle);
          p.tilt = Math.sin(p.tiltAngle - idx / 3) * 15;
          
          ctx.beginPath();
          ctx.lineWidth = p.r;
          ctx.strokeStyle = p.color;
          ctx.moveTo(p.x + p.tilt + p.r / 2, p.y);
          ctx.lineTo(p.x + p.tilt, p.y + p.tilt + p.r / 2);
          ctx.stroke();
        });
        
        particles = particles.filter(p => p.y < canvas.height);
        if (particles.length > 0) {
          requestAnimationFrame(draw);
        }
      }
      draw();
    }

    // Support Tab Key in editor
    document.getElementById('editor').addEventListener('keydown', function(e) {
      if (e.key === 'Tab') {
        e.preventDefault();
        const start = this.selectionStart;
        const end = this.selectionEnd;
        this.value = this.value.substring(0, start) + " " + this.value.substring(end);
        this.selectionStart = this.selectionEnd = start + 4;
        updateLineNumbers();
        
        // Save state immediately
        if (currentTabId !== "lesson") {
          const modeKey = `${currentModuleIndex}_${currentTabId}`;
          const currentMode = currentLabMode[modeKey] || "normal";
          codeCache[`${currentModuleIndex}_${currentTabId}_${currentMode}`] = this.value;
        } else {
          codeCache[`${currentModuleIndex}_lesson_step_${currentStepIndex}`] = this.value;
        }
        saveProgress();
      }
    });

    // Auto-save code on every keystroke
    document.getElementById('editor').addEventListener('input', function() {
      if (currentTabId !== "lesson") {
        const modeKey = `${currentModuleIndex}_${currentTabId}`;
        const currentMode = currentLabMode[modeKey] || "normal";
        codeCache[`${currentModuleIndex}_${currentTabId}_${currentMode}`] = this.value;
      } else {
        codeCache[`${currentModuleIndex}_lesson_step_${currentStepIndex}`] = this.value;
      }
      saveProgress();
      updateLineNumbers();
    });

    function updateLineNumbers() {
      const editor = document.getElementById("editor");
      const lineNumbers = document.getElementById("line-numbers");
      if (!editor || !lineNumbers) return;
      const lines = editor.value.split("\\n");
      const lineCount = lines.length;
      
      let numbers = [];
      for (let i = 1; i <= lineCount; i++) {
        numbers.push(i);
      }
      lineNumbers.textContent = numbers.join("\\n");
    }

    function syncScroll() {
      const editor = document.getElementById("editor");
      const lineNumbers = document.getElementById("line-numbers");
      if (!editor || !lineNumbers) return;
      lineNumbers.scrollTop = editor.scrollTop;
    }

    document.getElementById('editor').addEventListener('scroll', syncScroll);

    // Initialize App
    fetchCourseData();
  </script>
</body>
</html>
"""

class PortalHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress server logging to keep terminal clean
        pass

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_CONTENT.encode("utf-8"))
        elif parsed_path.path == "/api/data":
            try:
                with open("course_data.json", "r", encoding="utf-8") as f:
                    data = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(data.encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode("utf-8"))
        elif parsed_path.path == "/api/load_progress":
            try:
                progress_path = "progress.json"
                if os.path.exists(progress_path):
                    with open(progress_path, "r", encoding="utf-8") as f:
                        data = f.read()
                else:
                    data = json.dumps({
                        "currentModuleIndex": 0,
                        "currentStepIndex": 0,
                        "currentTabId": "lab_2",
                        "completedSteps": {},
                        "currentLabMode": {},
                        "usedHelpForCurrentLab": {},
                        "codeCache": {}
                    })
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(data.encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        try:
            body = json.loads(post_data)
        except Exception:
            self.send_response(400)
            self.end_headers()
            return

        if parsed_path.path == "/api/run":
            code = body.get("code", "")
            if "input(" in code or "input (" in code:
                # Handle interactive console execution
                temp_path = os.path.join(os.getcwd(), "interactive_run.py")
                with open(temp_path, "w", encoding="utf-8") as f:
                    f.write(code)
                
                # Launch a real Windows command prompt window
                if sys.platform == "win32":
                    # Uses start cmd.exe /k which launches python and keeps terminal open
                    cmd = f'start cmd.exe /k ""{sys.executable}" interactive_run.py"'
                    subprocess.Popen(cmd, shell=True)
                else:
                    # Fallback command execution
                    subprocess.Popen([sys.executable, "interactive_run.py"])
                
                self.send_json_response({
                    "stdout": "[Terminal launched for interactive input... Check your taskbar!]\n",
                    "stderr": "",
                    "interactive": True
                })
            else:
                # Background execution
                stdout, stderr, exit_code = run_code_in_background(code)
                self.send_json_response({
                    "stdout": stdout,
                    "stderr": stderr,
                    "interactive": False
                })

        elif parsed_path.path == "/api/save_progress":
            try:
                with open("progress.json", "w", encoding="utf-8") as f:
                    f.write(post_data)
                self.send_json_response({"success": True})
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode("utf-8"))
        elif parsed_path.path == "/api/test":
            code = body.get("code", "")
            test_code = body.get("test_code", "")
            full_code = code + "\n\n# --- AUTOMATED TESTS ---\n" + test_code
            stdout, stderr, exit_code = run_code_in_background(full_code)
            
            passed = "EXERCISE_PASSED" in stdout
            clean_stdout = stdout.replace("EXERCISE_PASSED\n", "").replace("EXERCISE_PASSED", "")
            
            self.send_json_response({
                "passed": passed,
                "stdout": clean_stdout,
                "stderr": stderr
            })
        else:
            self.send_response(404)
            self.end_headers()

    def send_json_response(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

def run_code_in_background(code):
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w", encoding="utf-8") as temp_file:
        temp_file.write(code)
        temp_path = temp_file.name

    try:
        env = os.environ.copy()
        env["PYTHONPATH"] = os.getcwd()
        res = subprocess.run([sys.executable, temp_path], capture_output=True, text=True, timeout=3, env=env)
        stdout = res.stdout
        stderr = res.stderr
        exit_code = res.returncode
    except subprocess.TimeoutExpired:
        stdout = ""
        stderr = "Timeout Error: Your code took too long to run. Did you create an infinite loop?"
        exit_code = -1
    finally:
        try:
            os.remove(temp_path)
        except Exception:
            pass
            
    return stdout, stderr, exit_code

def start_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), PortalHandler) as httpd:
        print(f"Server started on http://localhost:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    # Start web server in a separate thread so we can launch the browser
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()

    # Wait a brief moment for the server to bind
    time.sleep(0.5)

    # Automatically open the learning portal web browser window
    if "PORTAL_NO_OPEN" not in os.environ:
        print("Launching your interactive Python learning portal...")
        webbrowser.open(f"http://localhost:{PORT}")
    else:
        print("PORTAL_NO_OPEN is set. Skipping browser auto-open.")

    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping Python Learning Portal. Happy coding!")
        sys.exit(0)
