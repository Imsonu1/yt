import React, { useState, useEffect, useRef } from 'react';
import { Play, Sparkles, Loader2, Download, Image as ImageIcon, Monitor, Code, Palette, Grid, AlertCircle } from 'lucide-react';

// Simple syntax highlighting helper for Python
const highlightCode = (code) => {
  if (!code) return [];

  const tokens = [];
  const regex = /(\b(def|class|import|from|return|if|else|elif|for|while|try|except|print|True|False|None|and|or|not|in|is|as|with|yield|lambda|global|nonlocal|assert|del|pass|break|continue|raise)\b)|("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')|(#.*)|(\b\d+\b)|([(){}\[\]])|(\w+)/g;

  let lastIndex = 0;
  let match;

  while ((match = regex.exec(code)) !== null) {
    if (match.index > lastIndex) {
      tokens.push({ type: 'text', content: code.slice(lastIndex, match.index) });
    }

    if (match[2]) tokens.push({ type: 'keyword', content: match[0] });
    else if (match[3]) tokens.push({ type: 'string', content: match[0] });
    else if (match[4]) tokens.push({ type: 'comment', content: match[0] });
    else if (match[5]) tokens.push({ type: 'number', content: match[0] });
    else if (match[6]) tokens.push({ type: 'punctuation', content: match[0] });
    else if (match[7]) tokens.push({ type: 'identifier', content: match[0] });
    else tokens.push({ type: 'text', content: match[0] });

    lastIndex = regex.lastIndex;
  }

  if (lastIndex < code.length) {
    tokens.push({ type: 'text', content: code.slice(lastIndex) });
  }

  return tokens;
};

export default function App() {
  // Mode State: 'quiz' or 'visual'
  const [mode, setMode] = useState('quiz');

  const [headerText, setHeaderText] = useState("Python Quiz 💎");
  const [footerText, setFooterText] = useState("Comment your answer below 👇");
  const [code, setCode] = useState(`Click AI Generate to get started!`);

  // For Visual Mode
  const [visualTitle, setVisualTitle] = useState("Particle Wave");
  const [visualJS, setVisualJS] = useState(`
    const t = time / 1000;
    const cols = 10;
    const rows = 10;
    const cellW = width / cols;
    const cellH = height / rows;
    
    for(let i=0; i<cols; i++) {
      for(let j=0; j<rows; j++) {
        const x = i * cellW + cellW/2;
        const y = j * cellH + cellH/2;
        const dist = Math.sqrt((x-width/2)**2 + (y-height/2)**2);
        const radius = (Math.sin(t * 2 + dist * 0.05) + 1) * 10;
        
        ctx.beginPath();
        ctx.fillStyle = \`hsl(\${(dist * 0.5 + t * 50) % 360}, 70%, 60%)\`;
        ctx.arc(x, y, radius, 0, Math.PI*2);
        ctx.fill();
      }
    }
  `);

  const [bgStyle, setBgStyle] = useState('tech');
  const [fontSize, setFontSize] = useState(13);
  const [enableShake, setEnableShake] = useState(true);
  const [enableCRT, setEnableCRT] = useState(false);
  const [glowIntensity, setGlowIntensity] = useState(0.8);
  const [bgImage, setBgImage] = useState(null);

  // AI States
  const [isGeneratingCode, setIsGeneratingCode] = useState(false);
  const [isGeneratingImage, setIsGeneratingImage] = useState(false);
  const [aiError, setAiError] = useState("");

  // Export State
  const [isExporting, setIsExporting] = useState(false);
  const [exportProgress, setExportProgress] = useState(0);

  // Floating particles (for Quiz mode)
  const [particles, setParticles] = useState([]);

  // Refs
  const canvasRef = useRef(null); // For export
  const previewCanvasRef = useRef(null); // For live preview
  const bgImageRef = useRef(null);

  // ⚠️ IMPORTANT: PASTE YOUR API KEY HERE
  const apiKey = "AIzaSyAOJg3WBGbR2JbgDmkb_Vx2jjbxwx1chuE";

  useEffect(() => {
    const symbols = ['{ }', 'def', 'print', '#', '[]', '<>', '()', 'py', '??', '!!'];
    const newParticles = Array.from({ length: 20 }).map((_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      symbol: symbols[Math.floor(Math.random() * symbols.length)],
      duration: 15 + Math.random() * 20,
      delay: Math.random() * 5,
      size: 15 + Math.random() * 25,
      opacity: 0.1 + Math.random() * 0.2
    }));
    setParticles(newParticles);
  }, []);

  // --- Live Preview Loop ---
  useEffect(() => {
    let animationId;
    const startTime = performance.now();

    const loop = (now) => {
      const elapsed = now - startTime;
      const canvas = previewCanvasRef.current;
      if (canvas) {
        const ctx = canvas.getContext('2d');
        renderFrame(ctx, elapsed, canvas.width, canvas.height);
      }
      animationId = requestAnimationFrame(loop);
    };

    animationId = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(animationId);
  }, [headerText, footerText, code, bgStyle, fontSize, enableShake, enableCRT, glowIntensity, particles, mode, visualJS, bgImage, visualTitle]);

  // --- Gemini API Helpers ---
  const callGemini = async (prompt, systemInstruction = "") => {
    setAiError("");
    if (!apiKey) {
      setAiError("API Key missing! Check src/App.js");
      return null;
    }
    try {
      const response = await fetch(
        `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key=${apiKey}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            contents: [{ parts: [{ text: prompt }] }],
            systemInstruction: { parts: [{ text: systemInstruction }] },
            generationConfig: { responseMimeType: "application/json" } // Enforce JSON
          }),
        }
      );
      if (!response.ok) throw new Error("AI request failed");
      const data = await response.json();
      return JSON.parse(data.candidates?.[0]?.content?.parts?.[0]?.text || "{}");
    } catch (error) {
      console.error("Gemini API Error:", error);
      setAiError("AI service unavailable.");
      return null;
    }
  };

  const handleAIMagicCode = async () => {
    if (isGeneratingCode) return;
    setIsGeneratingCode(true);

    try {
      if (mode === 'quiz') {
        const systemPrompt = `You are a Python expert creating engaging 'Guess the Output' quizzes. 
            Generate a tricky Python code snippet (e.g. scope, mutable defaults, list comprehension). 
            Return JSON: { "code": "full python code with question and options A/B/C/D" }`;

        const result = await callGemini("Generate a tricky python quiz question.", systemPrompt);
        if (result && result.code) {
          setCode(result.code);
        }
      } else {
        // VISUAL MODE AI GENERATION
        const systemPrompt = `You are a Creative Coder. 
            Goal: Create a stunning visual animation logic.
            
            Return JSON with three fields:
            1. "title": A short cool title (e.g. "Neon Vortex").
            2. "python_code": A VERY SHORT Python script (MAX 8-10 LINES).
               - DO NOT INCLUDE IMPORTS like 'import turtle' or 'import math'. Assume they exist.
               - Just show the logic loop or variables.
               - MUST fit in a vertical video box without scrolling.
            3. "javascript_renderer": A valid JavaScript function body string. The function signature is (ctx, width, height, time). 'time' is in ms.
               - Draw the pattern described.
               - Use 'ctx' (CanvasRenderingContext2D).
               - Use neon colors.
               - Make it animated using 'time'.
               - Example: "const t = time/500; ctx.fillStyle='cyan'; ctx.fillRect(Math.sin(t)*50 + width/2, height/2, 20, 20);"
            `;

        const result = await callGemini("Generate a random visually stunning code demo.", systemPrompt);
        if (result) {
          if (result.title) setVisualTitle(result.title);
          if (result.python_code) setCode(result.python_code);
          if (result.javascript_renderer) setVisualJS(result.javascript_renderer);
        }
      }
    } catch (e) {
      setAiError("Failed to generate content.");
    }

    setIsGeneratingCode(false);
  };

  // --- LOCAL GENERATIVE ART ALGORITHMS ---
  // This runs if API fails or is used as primary for cool tech backgrounds
  const generateProceduralBackground = () => {
    const canvas = document.createElement('canvas');
    canvas.width = 1080;
    canvas.height = 1920;
    const ctx = canvas.getContext('2d');
    const w = 1080;
    const h = 1920;

    // Pick a random style
    const styles = ['matrix', 'cyber_grid', 'nebula'];
    const style = styles[Math.floor(Math.random() * styles.length)];

    if (style === 'matrix') {
      // Dark Base
      ctx.fillStyle = '#020617';
      ctx.fillRect(0, 0, w, h);
      // Columns
      const cols = 50;
      const colW = w / cols;
      for (let i = 0; i < cols; i++) {
        const len = Math.random() * h;
        const speed = Math.random() * 0.5 + 0.5;
        const x = i * colW;

        // Gradient Stream
        const grad = ctx.createLinearGradient(x, 0, x, len);
        grad.addColorStop(0, 'rgba(0, 255, 100, 0)');
        grad.addColorStop(1, 'rgba(0, 255, 100, 0.3)');

        ctx.fillStyle = grad;
        ctx.fillRect(x, 0, colW - 2, len);

        // Random chars
        ctx.fillStyle = 'rgba(0, 255, 100, 0.5)';
        ctx.font = '15px monospace';
        for (let j = 0; j < 20; j++) {
          if (Math.random() > 0.8) {
            ctx.fillText(String.fromCharCode(0x30A0 + Math.random() * 96), x, Math.random() * len);
          }
        }
      }
    } else if (style === 'cyber_grid') {
      // Retro Grid
      const hue = Math.floor(Math.random() * 60) + 260; // Purple/Blue range
      const grad = ctx.createLinearGradient(0, 0, 0, h);
      grad.addColorStop(0, `hsl(${hue}, 60%, 10%)`);
      grad.addColorStop(1, `hsl(${hue - 40}, 60%, 5%)`);
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, w, h);

      // Perspective Grid lines
      ctx.strokeStyle = `hsla(${hue}, 80%, 70%, 0.15)`;
      ctx.lineWidth = 2;

      // Horizon
      const horizon = h * 0.3;

      // Sun
      const sunGrad = ctx.createLinearGradient(0, horizon - 200, 0, horizon + 100);
      sunGrad.addColorStop(0, '#f59e0b');
      sunGrad.addColorStop(1, 'rgba(245, 158, 11, 0)');
      ctx.fillStyle = sunGrad;
      ctx.beginPath(); ctx.arc(w / 2, horizon, 150, 0, Math.PI, true); ctx.fill();

      // Vertical converging lines
      for (let x = -w; x < w * 2; x += 80) {
        ctx.beginPath();
        ctx.moveTo(x, h);
        ctx.lineTo(w / 2, horizon);
        ctx.stroke();
      }
      // Horizontal lines
      for (let y = horizon; y < h; y += (y - horizon) * 0.1 + 5) {
        ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke();
      }

    } else {
      // Nebula / Smoke
      ctx.fillStyle = '#000000';
      ctx.fillRect(0, 0, w, h);

      for (let i = 0; i < 50; i++) {
        const x = Math.random() * w;
        const y = Math.random() * h;
        const r = Math.random() * 400 + 100;
        const hue = Math.floor(Math.random() * 360);

        const grad = ctx.createRadialGradient(x, y, 0, x, y, r);
        grad.addColorStop(0, `hsla(${hue}, 70%, 60%, 0.1)`);
        grad.addColorStop(1, `hsla(${hue}, 70%, 60%, 0)`);

        ctx.fillStyle = grad;
        ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fill();
      }
    }

    return canvas.toDataURL('image/png');
  };

  const handleGenerateBackground = async () => {
    if (isGeneratingImage) return;
    setIsGeneratingImage(true);
    setAiError("");

    let generatedImage = null;

    // Try API First (imagen-3.0)
    if (apiKey) {
      try {
        const prompt = "Vertical abstract background for coding social media reel, dark blue and purple technology gradient, subtle python code symbols, matrix rain style but minimalist, cinematic lighting, 8k, vertical 9:16 aspect ratio";
        const response = await fetch(
          `https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-001:predict?key=${apiKey}`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              instances: [{ prompt: prompt }],
              parameters: { sampleCount: 1, aspectRatio: "9:16" }
            })
          }
        );

        if (response.ok) {
          const data = await response.json();
          const base64Image = data.predictions?.[0]?.bytesBase64Encoded;
          if (base64Image) {
            generatedImage = `data:image/png;base64,${base64Image}`;
          }
        } else {
          console.warn("API Generation failed, falling back to local engine.");
        }
      } catch (e) {
        console.error(e);
      }
    }

    // FAIL-SAFE: If API failed or no key, use Local Procedural Generator
    if (!generatedImage) {
      generatedImage = generateProceduralBackground();
      if (!apiKey) setAiError("Generated locally (No API Key).");
      else setAiError("API Failed. Generated locally.");
    }

    if (generatedImage) {
      setBgImage(generatedImage);
      const img = new Image();
      img.src = generatedImage;
      bgImageRef.current = img;
    }

    setIsGeneratingImage(false);
  };

  // --- Canvas Rendering & Export Logic ---

  const drawRoundedRect = (ctx, x, y, width, height, radius) => {
    ctx.beginPath();
    ctx.moveTo(x + radius, y);
    ctx.lineTo(x + width - radius, y);
    ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
    ctx.lineTo(x + width, y + height - radius);
    ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
    ctx.lineTo(x + radius, y + height);
    ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
    ctx.lineTo(x, y + radius);
    ctx.quadraticCurveTo(x, y, x + radius, y);
    ctx.closePath();
  };

  const renderFrame = (ctx, time, width, height) => {
    // 1. Clear Screen
    ctx.clearRect(0, 0, width, height);

    // Camera Shake Effect
    let shakeX = 0;
    let shakeY = 0;
    if (enableShake) {
      const shakeIntensity = 1.5;
      shakeX = (Math.sin(time / 40) + Math.cos(time / 70)) * shakeIntensity;
      shakeY = (Math.cos(time / 50) + Math.sin(time / 80)) * shakeIntensity;
      ctx.save();
      ctx.translate(shakeX, shakeY);
    }

    // 2. Background
    if (bgImageRef.current && bgImageRef.current.complete) {
      const img = bgImageRef.current;
      const scale = Math.max(width / img.width, height / img.height);
      const x = (width / 2) - (img.width / 2) * scale;
      const y = (height / 2) - (img.height / 2) * scale;
      ctx.drawImage(img, x, y, img.width * scale, img.height * scale);
      ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
      ctx.fillRect(0, 0, width, height);
    } else {
      const gradient = ctx.createRadialGradient(width / 2, 0, 0, width / 2, 0, height);
      gradient.addColorStop(0, '#1e40af');
      gradient.addColorStop(0.5, '#0f172a');
      gradient.addColorStop(1, '#020617');
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, width, height);

      ctx.strokeStyle = 'rgba(255,255,255,0.05)';
      ctx.lineWidth = 2;
      const gridSize = 60;
      for (let gx = 0; gx < width; gx += gridSize) { ctx.beginPath(); ctx.moveTo(gx, 0); ctx.lineTo(gx, height); ctx.stroke(); }
      for (let gy = 0; gy < height; gy += gridSize) { ctx.beginPath(); ctx.moveTo(0, gy); ctx.lineTo(width, gy); ctx.stroke(); }

      if (mode === 'quiz') {
        particles.forEach(p => {
          ctx.fillStyle = 'rgba(255, 255, 255, 0.05)';
          ctx.font = `${p.size * 2}px monospace`;
          const yOffset = Math.sin(time / 1500 + p.id) * 40;
          ctx.fillText(p.symbol, (p.x / 100) * width, (p.y / 100) * height + yOffset);
        });
      }
    }

    // --- Common Animations ---
    const introDuration = 1000;

    // --- MODE: VISUAL LAYOUT ---
    if (mode === 'visual') {
      const titleText = visualTitle || headerText;

      // 1. Title (Top) - Beautified with Python Gradient & Glow
      const headerY = height * 0.08;
      ctx.save();
      ctx.textAlign = 'center';
      ctx.textBaseline = 'top';
      ctx.font = '900 64px sans-serif';

      const textWidth = ctx.measureText(titleText.toUpperCase()).width;
      const headerGradient = ctx.createLinearGradient(width / 2 - textWidth / 2, 0, width / 2 + textWidth / 2, 0);
      headerGradient.addColorStop(0, '#3b82f6'); // Python Blue
      headerGradient.addColorStop(1, '#fbbf24'); // Python Yellow
      ctx.fillStyle = headerGradient;

      ctx.shadowColor = `rgba(251, 191, 36, ${glowIntensity})`;
      ctx.shadowBlur = 30 * glowIntensity + 15;

      ctx.fillText(titleText.toUpperCase(), width / 2, headerY);
      ctx.restore();

      // 2. Code Box (Top Half) - Typing Effect
      const codeBoxTop = height * 0.18;
      const codeBoxHeight = height * 0.35;
      const boxWidth = width * 0.90;
      const boxX = width / 2;

      ctx.save();
      ctx.fillStyle = 'rgba(15, 23, 42, 0.85)';

      ctx.beginPath();
      drawRoundedRect(ctx, boxX - boxWidth / 2, codeBoxTop, boxWidth, codeBoxHeight, 30);
      ctx.fill();
      ctx.save();
      ctx.clip();

      // Auto-Fit Font
      let activeFontSize = fontSize * 1.8;
      const paddingX = 40;
      const availableWidth = boxWidth - (paddingX * 2);
      const availableHeight = codeBoxHeight - 80;

      const calculateTotalLines = (testFontSize) => {
        ctx.font = `600 ${testFontSize}px monospace`;
        const lines = code.split('\n');
        let totalLines = 0;
        lines.forEach(line => {
          const lineWidth = ctx.measureText(line).width;
          totalLines += Math.max(1, Math.ceil(lineWidth / availableWidth));
        });
        return totalLines;
      };

      for (let i = 0; i < 10; i++) {
        const lineCount = calculateTotalLines(activeFontSize);
        const totalHeight = lineCount * (activeFontSize * 1.5);
        if (totalHeight > availableHeight) {
          activeFontSize *= 0.9;
        } else {
          break;
        }
      }
      activeFontSize = Math.max(10, activeFontSize);

      ctx.font = `600 ${activeFontSize}px monospace`;
      ctx.textAlign = 'left';
      ctx.textBaseline = 'top';

      const startTextX = (boxX - boxWidth / 2) + paddingX;
      let cursorX = startTextX;
      let cursorY = codeBoxTop + 60;
      const lineHeight = activeFontSize * 1.5;

      // Typing Logic
      const typeStart = 500;
      const typeSpeed = 30;
      const totalChars = code.length;
      const charsToShow = Math.max(0, Math.floor((time - typeStart) / typeSpeed));
      let charCount = 0;

      const tokens = highlightCode(code);
      tokens.forEach(token => {
        if (token.type === 'keyword') ctx.fillStyle = '#c084fc';
        else if (token.type === 'string') ctx.fillStyle = '#4ade80';
        else if (token.type === 'comment') ctx.fillStyle = '#94a3b8';
        else if (token.type === 'number') ctx.fillStyle = '#60a5fa';
        else if (token.type === 'punctuation') ctx.fillStyle = '#fbbf24';
        else if (token.type === 'identifier') ctx.fillStyle = '#93c5fd';
        else ctx.fillStyle = '#e2e8f0';

        const text = token.content;
        const lines = text.split('\n');
        lines.forEach((line, lineIndex) => {
          const words = line.split(/(\s+)/);
          words.forEach((word) => {
            const wordWidth = ctx.measureText(word).width;
            if (cursorX + wordWidth > startTextX + availableWidth) {
              cursorX = startTextX;
              cursorY += lineHeight;
            }
            for (let i = 0; i < word.length; i++) {
              if (charCount < charsToShow) {
                ctx.fillText(word[i], cursorX, cursorY);
              }
              cursorX += ctx.measureText(word[i]).width;
              charCount++;
            }
          });
          if (lineIndex < lines.length - 1) {
            cursorX = startTextX;
            cursorY += lineHeight;
            charCount++;
          }
        });
      });
      ctx.restore();

      // Draw Border & Dots
      ctx.strokeStyle = `rgba(255,255,255,${0.2})`;
      ctx.lineWidth = 2;
      drawRoundedRect(ctx, boxX - boxWidth / 2, codeBoxTop, boxWidth, codeBoxHeight, 30);
      ctx.stroke();

      const dotY = codeBoxTop + 35;
      const startDotX = (boxX - boxWidth / 2) + 35;
      ctx.fillStyle = '#ef4444'; ctx.beginPath(); ctx.arc(startDotX, dotY, 10, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = '#eab308'; ctx.beginPath(); ctx.arc(startDotX + 30, dotY, 10, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = '#22c55e'; ctx.beginPath(); ctx.arc(startDotX + 60, dotY, 10, 0, Math.PI * 2); ctx.fill();

      ctx.restore();

      // 3. Output Box
      const outBoxTop = codeBoxTop + codeBoxHeight + 20;
      const outBoxHeight = height * 0.40;

      const typingFinishTime = typeStart + (totalChars * typeSpeed) + 500;
      const showOutput = time > typingFinishTime;
      const fadeProgress = showOutput ? Math.min((time - typingFinishTime) / 1000, 1) : 0;

      ctx.save();
      drawRoundedRect(ctx, boxX - boxWidth / 2, outBoxTop, boxWidth, outBoxHeight, 30);
      ctx.clip();

      ctx.fillStyle = '#000000';
      ctx.fillRect(boxX - boxWidth / 2, outBoxTop, boxWidth, outBoxHeight);

      if (visualJS && showOutput) {
        try {
          ctx.globalAlpha = fadeProgress;
          ctx.translate(boxX - boxWidth / 2, outBoxTop);
          const animTime = time - typingFinishTime;
          const drawFn = new Function('ctx', 'width', 'height', 'time', visualJS);
          drawFn(ctx, boxWidth, outBoxHeight, animTime);
        } catch (e) { }
      } else {
        ctx.fillStyle = '#fbbf24';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.font = 'italic 700 32px sans-serif';
        ctx.globalAlpha = 0.6 + Math.sin(time / 200) * 0.4;

        const waitText = visualJS ? "WAIT FOR OUTPUT... 🚀" : "Click 'AI Generate'";
        ctx.fillText(waitText, 0 + boxWidth / 2 + (boxX - boxWidth / 2), 0 + outBoxHeight / 2 + outBoxTop);
      }
      ctx.restore();

      // Stroke Border
      ctx.save();
      drawRoundedRect(ctx, boxX - boxWidth / 2, outBoxTop, boxWidth, outBoxHeight, 30);

      const borderAlpha = 0.5 + (showOutput ? (Math.sin(time / 500) * 0.2) : 0);
      ctx.strokeStyle = `rgba(56, 189, 248, ${borderAlpha})`;
      ctx.lineWidth = 3;
      ctx.stroke();

      ctx.fillStyle = `rgba(56, 189, 248, ${0.5 + (fadeProgress * 0.5)})`;
      ctx.font = 'bold 20px sans-serif';
      ctx.textAlign = 'right';
      ctx.fillText("OUTPUT", boxX + boxWidth / 2 - 20, outBoxTop + 30);
      ctx.restore();

    }
    // --- MODE: QUIZ LAYOUT ---
    else {
      const headerY = height * 0.08;
      let headerX = width / 2;
      let headerOpacity = 1;

      if (time < introDuration) {
        const progress = Math.min(time / introDuration, 1);
        const ease = 1 - Math.pow(1 - progress, 3);
        headerX = width / 2 + (300 * (1 - ease));
        headerOpacity = ease;
      }

      ctx.save();
      ctx.textAlign = 'center';
      ctx.textBaseline = 'top';
      ctx.font = '900 80px sans-serif';
      ctx.globalAlpha = headerOpacity;

      const textWidth = ctx.measureText(headerText.toUpperCase()).width;
      const textGradient = ctx.createLinearGradient(headerX - (textWidth / 2), 0, headerX + (textWidth / 2), 0);
      textGradient.addColorStop(0, '#fb923c');
      textGradient.addColorStop(1, '#fcd34d');
      ctx.fillStyle = textGradient;

      ctx.shadowColor = 'rgba(0, 0, 0, 0.5)';
      ctx.shadowBlur = 20;
      ctx.shadowOffsetY = 10;
      ctx.fillText(headerText.toUpperCase(), headerX, headerY);
      ctx.restore();

      const boxTop = height * 0.18;
      const boxHeight = height * 0.70;
      const boxWidth = width * 0.90;
      let boxX = width / 2;
      let boxOpacity = 1;

      if (time < 800) {
        const progress = Math.min(time / 800, 1);
        const ease = 1 - Math.pow(1 - progress, 3);
        boxX = width / 2 - (200 * (1 - ease));
        boxOpacity = ease;
      }

      ctx.save();
      ctx.translate(boxX, boxTop + boxHeight / 2);
      ctx.translate(-boxX, -(boxTop + boxHeight / 2));
      ctx.globalAlpha = boxOpacity;

      ctx.fillStyle = 'rgba(15, 23, 42, 0.9)'; // More opaque for quiz
      drawRoundedRect(ctx, boxX - boxWidth / 2, boxTop, boxWidth, boxHeight, 40);
      ctx.fill();
      ctx.strokeStyle = 'rgba(255,255,255,0.15)';
      ctx.lineWidth = 2;
      ctx.stroke();

      const dotY = boxTop + 45;
      const startDotX = (boxX - boxWidth / 2) + 45;
      ctx.fillStyle = '#ef4444'; ctx.beginPath(); ctx.arc(startDotX, dotY, 12, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = '#eab308'; ctx.beginPath(); ctx.arc(startDotX + 35, dotY, 12, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = '#22c55e'; ctx.beginPath(); ctx.arc(startDotX + 70, dotY, 12, 0, Math.PI * 2); ctx.fill();

      const typeStart = 1000;
      const typeSpeed = 30;
      const charsToShow = Math.max(0, Math.floor((time - typeStart) / typeSpeed));

      ctx.font = `600 ${fontSize * 2.6}px monospace`;
      ctx.textAlign = 'left';
      ctx.textBaseline = 'top';

      const tokens = highlightCode(code);
      const paddingX = 50;
      const startTextX = (boxX - boxWidth / 2) + paddingX;
      let cursorX = startTextX;
      let cursorY = boxTop + 100;
      const lineHeight = fontSize * 4;
      const maxTextWidth = boxWidth - (paddingX * 2);

      let charCount = 0;

      tokens.forEach(token => {
        if (token.type === 'keyword') ctx.fillStyle = '#c084fc';
        else if (token.type === 'string') ctx.fillStyle = '#4ade80';
        else if (token.type === 'comment') ctx.fillStyle = '#94a3b8';
        else if (token.type === 'number') ctx.fillStyle = '#60a5fa';
        else if (token.type === 'punctuation') ctx.fillStyle = '#fbbf24';
        else if (token.type === 'identifier') ctx.fillStyle = '#93c5fd';
        else ctx.fillStyle = '#e2e8f0';

        const parts = token.content.split('\n');
        parts.forEach((part, i) => {
          const words = part.split(/(\s+)/);
          words.forEach((word) => {
            const wordWidth = ctx.measureText(word).width;
            if (cursorX + wordWidth > startTextX + maxTextWidth) {
              cursorX = startTextX;
              cursorY += lineHeight;
            }
            for (let j = 0; j < word.length; j++) {
              if (charCount < charsToShow) ctx.fillText(word[j], cursorX, cursorY);
              cursorX += ctx.measureText(word[j]).width;
              charCount++;
            }
          });
          if (i < parts.length - 1) {
            cursorX = startTextX;
            cursorY += lineHeight;
            charCount++;
          }
        });
      });
      ctx.restore();

      // Footer
      ctx.save();
      ctx.textAlign = 'center';
      ctx.textBaseline = 'bottom';
      ctx.font = '600 40px sans-serif';
      ctx.fillStyle = '#cbd5e1';
      ctx.fillText(footerText, width / 2, height * 0.96);
      ctx.restore();
    }

    if (enableShake) ctx.restore();

    if (enableCRT) {
      ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
      for (let i = 0; i < height; i += 4) {
        ctx.fillRect(0, i, width, 2);
      }
      const gradient = ctx.createRadialGradient(width / 2, height / 2, height / 3, width / 2, height / 2, height);
      gradient.addColorStop(0, 'rgba(0,0,0,0)');
      gradient.addColorStop(1, 'rgba(0,0,0,0.4)');
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, width, height);
    }
  };

  const handleExportVideo = async () => {
    setIsExporting(true);
    setExportProgress(0);
    setAiError("");

    const canvas = canvasRef.current;
    if (!canvas) return;

    canvas.width = 1080;
    canvas.height = 1920;
    const ctx = canvas.getContext('2d');

    renderFrame(ctx, 0, 1080, 1920);

    // CALCULATE DURATION (Dynamic)
    let duration = 15000;
    if (mode === 'visual') {
      const typeStart = 500;
      const typeSpeed = 30;
      const totalChars = code.length;
      const typingFinishTime = typeStart + (totalChars * typeSpeed) + 500;
      // Ensure 8 seconds of output after typing finishes
      duration = Math.max(15000, typingFinishTime + 8000);
    }

    const canvasStream = canvas.captureStream(30);
    const recorder = new MediaRecorder(canvasStream, { mimeType: 'video/webm; codecs=vp9' });
    const chunks = [];

    recorder.ondataavailable = (e) => {
      if (e.data.size > 0) chunks.push(e.data);
    };

    recorder.onstop = () => {
      const blob = new Blob(chunks, { type: 'video/webm' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `python_${mode}_${Date.now()}.webm`;
      a.click();
      setIsExporting(false);
    };

    recorder.start();

    const startTime = performance.now();
    let animationId;

    const loop = (now) => {
      const elapsed = now - startTime;
      renderFrame(ctx, elapsed, 1080, 1920);
      setExportProgress(Math.min((elapsed / duration) * 100, 100));

      if (elapsed < duration) {
        animationId = requestAnimationFrame(loop);
      } else {
        recorder.stop();
        cancelAnimationFrame(animationId);
      }
    };
    requestAnimationFrame(loop);
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-4 font-sans flex flex-col md:flex-row gap-8 items-center md:items-start justify-center md:p-8">

      {/* Hidden Export Canvas */}
      <canvas ref={canvasRef} style={{ display: 'none' }} />

      {/* Settings Panel */}
      <div className="w-full md:w-1/3 max-w-md space-y-5 bg-gray-800 p-6 rounded-xl shadow-xl border border-gray-700">

        {/* Mode Switcher */}
        <div className="flex p-1 bg-gray-900 rounded-lg mb-4">
          <button
            onClick={() => setMode('quiz')}
            className={`flex-1 py-2 rounded-md text-sm font-bold flex items-center justify-center gap-2 transition-all ${mode === 'quiz' ? 'bg-blue-600 text-white shadow' : 'text-gray-400 hover:text-white'}`}
          >
            <Code size={16} /> Quiz Mode
          </button>
          <button
            onClick={() => setMode('visual')}
            className={`flex-1 py-2 rounded-md text-sm font-bold flex items-center justify-center gap-2 transition-all ${mode === 'visual' ? 'bg-purple-600 text-white shadow' : 'text-gray-400 hover:text-white'}`}
          >
            <Palette size={16} /> Visual Mode
          </button>
        </div>

        <div className="flex justify-between items-center border-b border-gray-700 pb-4">
          <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500 flex items-center gap-2">
            <Play className="text-purple-500" fill="currentColor" />
            Reel Builder
          </h1>
          {aiError && <span className="text-xs text-red-300 bg-red-900/30 px-2 py-1 rounded">{aiError}</span>}
        </div>

        <div className="space-y-4">
          {mode === 'quiz' && (
            <div>
              <label className="text-xs font-medium text-gray-400 uppercase">Header</label>
              <input
                type="text"
                value={headerText}
                onChange={(e) => setHeaderText(e.target.value)}
                className="w-full mt-1 bg-gray-900 border border-gray-700 rounded-lg p-2.5 focus:ring-2 focus:ring-blue-500 outline-none text-white font-bold"
                placeholder="Ex: Python quiz 💎"
              />
            </div>
          )}

          {/* In Visual Mode, Title is auto-generated but editable */}
          {mode === 'visual' && (
            <div>
              <label className="text-xs font-medium text-gray-400 uppercase">Visual Title</label>
              <input
                type="text"
                value={visualTitle}
                onChange={(e) => setVisualTitle(e.target.value)}
                className="w-full mt-1 bg-gray-900 border border-gray-700 rounded-lg p-2.5 focus:ring-2 focus:ring-purple-500 outline-none text-white font-bold"
                placeholder="Ex: Neon Helix"
              />
            </div>
          )}

          <div className="space-y-2">
            <div className="flex justify-between items-end mb-1">
              <label className="text-xs font-medium text-gray-400 uppercase">Code</label>
              <button
                onClick={handleAIMagicCode}
                disabled={isGeneratingCode}
                className="text-[10px] bg-purple-600/20 hover:bg-purple-600/40 text-purple-300 px-2 py-1 rounded flex items-center gap-1 transition-colors border border-purple-500/30"
              >
                {isGeneratingCode ? <Loader2 size={10} className="animate-spin" /> : <Sparkles size={10} />}
                AI Generate
              </button>
            </div>
            <textarea
              value={code}
              onChange={(e) => setCode(e.target.value)}
              className="w-full h-40 bg-gray-900 border border-gray-700 rounded-lg p-3 font-mono text-xs focus:ring-2 focus:ring-blue-500 outline-none resize-none text-gray-200 leading-relaxed"
              spellCheck="false"
              placeholder="Paste your code..."
            />
          </div>

          {mode === 'quiz' && (
            <div>
              <label className="text-xs font-medium text-gray-400 uppercase">Footer</label>
              <input
                type="text"
                value={footerText}
                onChange={(e) => setFooterText(e.target.value)}
                className="w-full mt-1 bg-gray-900 border border-gray-700 rounded-lg p-2.5 focus:ring-2 focus:ring-blue-500 outline-none text-gray-300"
              />
            </div>
          )}

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-medium text-gray-400 uppercase block mb-2">
                Font Size <span className="text-blue-400">({fontSize}px)</span>
              </label>
              <input
                type="range"
                min="10"
                max="24"
                value={fontSize}
                onChange={(e) => setFontSize(parseInt(e.target.value))}
                className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
              />
            </div>
            <div>
              <label className="text-xs font-medium text-gray-400 uppercase block mb-2">Background</label>
              <button
                onClick={handleGenerateBackground}
                disabled={isGeneratingImage}
                className="w-full py-1.5 bg-blue-600/20 hover:bg-blue-600/40 text-blue-300 rounded text-xs font-bold flex items-center justify-center gap-2 border border-blue-500/30"
              >
                {isGeneratingImage ? <Loader2 size={12} className="animate-spin" /> : <ImageIcon size={12} />}
                {isGeneratingImage ? 'Generating...' : 'AI Background'}
              </button>
            </div>
          </div>

          {/* Effects Section */}
          <div>
            <label className="text-xs font-medium text-gray-400 uppercase block mb-2">Visual Effects</label>
            <div className="grid grid-cols-2 gap-3 mb-2">
              <button
                onClick={() => setEnableCRT(!enableCRT)}
                className={`py-2 rounded text-xs font-bold border ${enableCRT ? 'bg-green-900/50 text-green-400 border-green-500/50' : 'bg-gray-700/50 text-gray-400 border-gray-600'}`}
              >
                <Monitor size={14} className="inline mr-1" /> CRT Scanline
              </button>
              <button
                onClick={() => setEnableShake(!enableShake)}
                className={`py-2 rounded text-xs font-bold border ${enableShake ? 'bg-orange-900/50 text-orange-400 border-orange-500/50' : 'bg-gray-700/50 text-gray-400 border-gray-600'}`}
              >
                ⚡ Camera Shake
              </button>
            </div>
            <div>
              <label className="text-[10px] text-gray-500 uppercase flex justify-between">
                Glow Intensity <span>{(glowIntensity * 100).toFixed(0)}%</span>
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={glowIntensity}
                onChange={(e) => setGlowIntensity(parseFloat(e.target.value))}
                className="w-full h-1.5 mt-1 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-amber-400"
              />
            </div>
          </div>

          <div className="pt-2 border-t border-gray-700">
            <button
              onClick={handleExportVideo}
              disabled={isExporting}
              className="w-full py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white rounded-lg font-bold flex items-center justify-center gap-2 shadow-lg transition-all transform active:scale-95 disabled:opacity-70 disabled:cursor-wait"
            >
              {isExporting ? <Loader2 size={20} className="animate-spin" /> : <Download size={20} />}
              {isExporting ? `Rendering... ${Math.round(exportProgress)}%` : 'Render & Download Video'}
            </button>
          </div>
        </div>
      </div>

      {/* Right Side: LIVE PREVIEW */}
      <div className="relative shrink-0 flex flex-col items-center">
        <div className="w-[360px] h-[640px] bg-black rounded-[40px] border-4 border-gray-700 overflow-hidden shadow-2xl relative">
          <canvas
            ref={previewCanvasRef}
            width={360}
            height={640}
            className="w-full h-full object-cover"
          />
          {/* Live indicator */}
          <div className="absolute top-4 right-4 flex items-center gap-1.5 bg-red-600/80 text-white text-[10px] font-bold px-2 py-0.5 rounded-full animate-pulse">
            <div className="w-1.5 h-1.5 bg-white rounded-full"></div> LIVE PREVIEW
          </div>
        </div>
        {mode === 'visual' && !visualJS && (
          <div className="mt-4 flex items-center gap-2 text-yellow-400 text-xs bg-yellow-900/20 p-2 rounded border border-yellow-500/20 max-w-[360px]">
            <AlertCircle size={16} /> Click "AI Generate" to create a visual effect!
          </div>
        )}
      </div>

    </div>
  );
}