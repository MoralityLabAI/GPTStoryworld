window.INKY_ART = {"enc_01":["#1b2a4a","#3a3f4a","#f4e6c8",50,62,34,"cobblestone alley",["char_pip"]],"enc_02":["#232c3e","#2e2a26","#d8c9a3",42,70,30,"bakery alley",["char_pip"]],"enc_03":["#2c3e5d","#4a4a42","#e8d9b0",55,55,38,"stone well coping",["char_pip"]],"enc_04":["#1f2d4d","#3d3a34","#f0e2c0",48,66,36,"stone well coping",["char_pip"]],"enc_05":["#26324a","#3f4636","#dfe8d0",52,58,40,"mossy well coping stone",["char_pip"]],"enc_06":["#1a2340","#33291f","#ffb84d",50,60,42,"amber baker's doorway",["char_pip"]],"enc_07":["#1e2a44","#33302c","#e6d3a8",46,64,32,"gray cat's head",["char_pip"]],"enc_08":["#2a2440","#2f2a24","#e8a34d",38,52,46,"village well",["char_old_fen","char_moon"]],"enc_09":["#25304a","#3a3f3a","#d9cfae",44,68,34,"laundry line",["char_pip"]],"enc_10":["#1c2740","#2e2b26","#cfc4a0",50,62,36,"laundry line",["char_pip"]],"enc_11":["#232c48","#33302a","#e3d3a4",50,58,52,"village gathering",["char_pip","char_mara","char_old_fen"]],"enc_12":["#1f2942","#2c2a26","#d8c49a",50,60,48,"village gathering",["char_pip","char_mara","char_old_fen"]],"enc_13":["#1a2340","#33291f","#ffc46b",50,62,40,"Mara's bakery window",["char_mara","char_pip"]],"enc_14":["#202c46","#3a3a32","#e8dfc0",40,64,44,"village well",["char_old_fen","char_moon"]],"enc_15":["#2a3350","#3d3a30","#e0d0a8",50,66,38,"crossroads",["char_pip","char_mara"]],"enc_16":["#1e2942","#38352c","#d5d0b8",52,56,42,"well's rim",["char_pip","char_moon"]],"end_return":["#3a4a6b","#5a5a48","#f2e6c4",50,60,36,"village well",["char_pip","char_moon"]],"end_keep":["#2c3a5e","#4a4438","#f5e9c0",50,58,40,"windowsill",["char_pip"]],"end_share":["#2e3a55","#3f4a2e","#e8d9a0",50,64,46,"small meadow",["char_pip","char_mara","char_old_fen"]],"end_fallback":["#141c33","#2a2620","#c9c2a8",50,62,34,"windowsill",["char_moon"]]};
// renderer.js - vanilla Canvas module for fable "The Hat That Held the Moon"
// window.drawScene(canvas, scene, cast)
// window.INKY_ART[scene.id] = [sky, ground, light, x%, y%, scale%, landmark, actorIds]
(function () {
  'use strict';

  var INKY_ART = {
    scene_01: ['#2b1b3d', '#3d2b1f', '#f7c873', 50, 18, 100, 'bakery window', ['char_pip', 'char_mara']],
    scene_02: ['#3a2a4a', '#4a3320', '#ffb347', 30, 55, 90, 'amber baker\'s doorway', ['char_mara']],
    scene_03: ['#241a33', '#33241a', '#ffd98a', 70, 60, 85, 'bakery alley', ['char_pip', 'char_mara']],
    scene_04: ['#1f2a3a', '#2e2a26', '#cfe3ff', 50, 65, 80, 'cobblestone alley', ['char_pip']],
    scene_05: ['#2a2440', '#3a3324', '#ffe9a8', 50, 50, 95, 'crossroads', ['char_pip', 'char_old_fen']],
    scene_06: ['#33203a', '#40301f', '#f2b8c6', 35, 45, 75, 'gray cat\'s head', ['char_pip']],
    scene_07: ['#2c3a2a', '#3f4a2a', '#fff3b0', 60, 40, 85, 'laundry line', ['char_pip', 'char_mara']],
    scene_08: ['#1e2a1e', '#2f3a24', '#b8e986', 45, 62, 90, 'mossy well coping stone', ['char_pip', 'char_old_fen']],
    scene_09: ['#243020', '#33402a', '#d8f0a0', 55, 58, 80, 'small meadow', ['char_pip']],
    scene_10: ['#2a2438', '#3a332a', '#ffd98a', 50, 55, 100, 'village gathering', ['char_pip', 'char_mara', 'char_old_fen', 'char_moon']],
    scene_11: ['#1c2a3a', '#2a3328', '#a8d8ff', 50, 60, 95, 'village well', ['char_pip', 'char_old_fen', 'char_moon']],
    scene_12: ['#141c2c', '#232a20', '#e8f4ff', 50, 35, 110, 'well\'s rim', ['char_moon', 'char_pip']],
    scene_13: ['#3a2a1a', '#4a3826', '#ffe9a8', 50, 70, 70, 'windowsill', ['char_pip', 'char_moon']]
  };

  function rr(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + w, y, r);
    ctx.closePath();
  }

  function drawLandmark(ctx, kind, W, H, s) {
    var cx = W * 0.5, base = H * 0.78;
    ctx.save();
    ctx.translate(cx, base);
    ctx.scale(s, s);
    if (kind === 'bakery window' || kind === "Mara's bakery window") {
      ctx.fillStyle = '#5a3a1e'; rr(ctx, -70, -150, 140, 130, 6); ctx.fill();
      ctx.fillStyle = '#ffd98a'; rr(ctx, -52, -132, 104, 92, 4); ctx.fill();
      ctx.strokeStyle = '#5a3a1e'; ctx.lineWidth = 6;
      ctx.beginPath(); ctx.moveTo(0, -132); ctx.lineTo(0, -40); ctx.moveTo(-52, -86); ctx.lineTo(52, -86); ctx.stroke();
      ctx.fillStyle = '#8a5a2a'; ctx.fillRect(-80, -22, 160, 12);
    } else if (kind === "amber baker's doorway") {
      ctx.fillStyle = '#6a3a14'; rr(ctx, -55, -160, 110, 160, 40); ctx.fill();
      ctx.fillStyle = '#ffb347'; rr(ctx, -38, -140, 76, 140, 30); ctx.fill();
      ctx.fillStyle = '#3a1e08'; ctx.beginPath(); ctx.arc(22, -70, 5, 0, 7); ctx.fill();
    } else if (kind === 'bakery alley') {
      ctx.fillStyle = '#4a3220'; ctx.fillRect(-110, -170, 70, 170); ctx.fillRect(40, -170, 70, 170);
      ctx.fillStyle = '#6a4a28'; ctx.fillRect(-110, -170, 70, 18); ctx.fillRect(40, -170, 70, 18);
      ctx.fillStyle = '#ffd98a'; ctx.fillRect(-88, -120, 26, 34); ctx.fillRect(62, -120, 26, 34);
    } else if (kind === 'cobblestone alley') {
      ctx.fillStyle = '#3a3630'; ctx.fillRect(-120, -40, 240, 40);
      ctx.fillStyle = '#55504a';
      for (var i = 0; i < 5; i++) for (var j = 0; j < 3; j++) { ctx.beginPath(); ctx.ellipse(-100 + i * 50 + (j % 2) * 20, -28 + j * 12, 16, 6, 0, 0, 7); ctx.fill(); }
    } else if (kind === 'crossroads') {
      ctx.fillStyle = '#4a4030'; ctx.fillRect(-130, -30, 260, 30); ctx.fillRect(-30, -150, 60, 150);
      ctx.fillStyle = '#5a5040'; ctx.fillRect(-130, -30, 260, 8);
    } else if (kind === "gray cat's head") {
      ctx.fillStyle = '#6a6a72'; ctx.beginPath(); ctx.arc(0, -80, 55, 0, 7); ctx.fill();
      ctx.beginPath(); ctx.moveTo(-40, -115); ctx.lineTo(-28, -160); ctx.lineTo(-8, -122); ctx.moveTo(40, -115); ctx.lineTo(28, -160); ctx.lineTo(8, -122); ctx.fill();
      ctx.fillStyle = '#f2c14e'; ctx.beginPath(); ctx.arc(-18, -82, 6, 0, 7); ctx.arc(18, -82, 6, 0, 7); ctx.fill();
    } else if (kind === 'laundry line') {
      ctx.strokeStyle = '#d8cfc0'; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(-120, -140); ctx.quadraticCurveTo(0, -110, 120, -140); ctx.stroke();
      var cols = ['#e8e0d0', '#c46a5a', '#5a7a9a', '#e0c060'];
      for (var k = 0; k < 4; k++) { ctx.fillStyle = cols[k]; ctx.fillRect(-90 + k * 55, -128 + Math.sin(k) * 6, 30, 42); }
    } else if (kind === 'mossy well coping stone' || kind === 'stone well coping') {
      ctx.fillStyle = '#5a5a52'; ctx.beginPath(); ctx.ellipse(0, -60, 85, 26, 0, 0, 7); ctx.fill();
      ctx.fillStyle = '#3a3a34'; ctx.beginPath(); ctx.ellipse(0, -60, 55, 14, 0, 0, 7); ctx.fill();
      ctx.fillStyle = '#4a6a2a'; ctx.beginPath(); ctx.ellipse(-40, -72, 18, 7, 0, 0, 7); ctx.ellipse(35, -70, 14, 6, 0, 0, 7); ctx.fill();
    } else if (kind === 'small meadow') {
      ctx.fillStyle = '#3f5a24'; ctx.beginPath(); ctx.ellipse(0, -20, 130, 26, 0, 0, 7); ctx.fill();
      ctx.strokeStyle = '#6a9a3a'; ctx.lineWidth = 3;
      for (var g = -4; g <= 4; g++) { ctx.beginPath(); ctx.moveTo(g * 28, -30); ctx.quadraticCurveTo(g * 28 + 6, -55, g * 28 + 2, -70); ctx.stroke(); }
    } else if (kind === 'village gathering') {
      ctx.fillStyle = '#5a4632'; ctx.fillRect(-120, -120, 60, 120); ctx.fillRect(60, -120, 60, 120);
      ctx.fillStyle = '#7a5a3a'; ctx.beginPath(); ctx.moveTo(-130, -120); ctx.lineTo(-90, -165); ctx.lineTo(-30, -120); ctx.moveTo(50, -120); ctx.lineTo(90, -165); ctx.lineTo(130, -120); ctx.fill();
    } else if (kind === 'village well') {
      ctx.fillStyle = '#4a4a44'; ctx.fillRect(-70, -110, 140, 110);
      ctx.fillStyle = '#5a5a52'; ctx.beginPath(); ctx.ellipse(0, -110, 85, 22, 0, 0, 7); ctx.fill();
      ctx.fillStyle = '#2a2a26'; ctx.beginPath(); ctx.ellipse(0, -110, 55, 12, 0, 0, 7); ctx.fill();
      ctx.strokeStyle = '#3a2a1a'; ctx.lineWidth = 8; ctx.beginPath(); ctx.moveTo(-85, -110); ctx.lineTo(-85, -175); ctx.moveTo(85, -110); ctx.lineTo(85, -175); ctx.stroke();
      ctx.fillStyle = '#6a4a28'; ctx.beginPath(); ctx.moveTo(-100, -175); ctx.lineTo(0, -215); ctx.lineTo(100, -175); ctx.closePath(); ctx.fill();
    } else if (kind === "well's rim") {
      ctx.fillStyle = '#5a5a52'; ctx.beginPath(); ctx.ellipse(0, -70, 95, 30, 0, 0, 7); ctx.fill();
      ctx.fillStyle = '#141c2c'; ctx.beginPath(); ctx.ellipse(0, -70, 62, 17, 0, 0, 7); ctx.fill();
      ctx.fillStyle = '#7a7a70'; ctx.beginPath(); ctx.ellipse(-30, -78, 20, 6, 0, 0, 7); ctx.fill();
    } else if (kind === 'windowsill') {
      ctx.fillStyle = '#6a4a28'; ctx.fillRect(-110, -60, 220, 18);
      ctx.fillStyle = '#4a3018'; ctx.fillRect(-110, -42, 220, 10);
      ctx.fillStyle = '#8a6a3a'; ctx.fillRect(-110, -60, 220, 6);
    }
    ctx.restore();
  }

  function drawPip(ctx, x, y, s, t) {
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
    ctx.fillStyle = '#5a5a62';
    ctx.beginPath(); ctx.ellipse(0, -28, 22, 26, 0, 0, 7); ctx.fill();
    ctx.beginPath(); ctx.arc(0, -62, 17, 0, 7); ctx.fill();
    ctx.beginPath(); ctx.moveTo(-13, -72); ctx.lineTo(-9, -88); ctx.lineTo(-2, -74); ctx.moveTo(13, -72); ctx.lineTo(9, -88); ctx.lineTo(2, -74); ctx.fill();
    ctx.fillStyle = '#f2c14e'; ctx.beginPath(); ctx.arc(-6, -62, 3.4, 0, 7); ctx.fill();
    ctx.strokeStyle = '#2a2a30'; ctx.lineWidth = 1.6; ctx.beginPath(); ctx.arc(2, -54, 5, 0.15 * Math.PI, 0.85 * Math.PI); ctx.stroke();
    ctx.strokeStyle = '#5a5a62'; ctx.lineWidth = 5; ctx.beginPath(); ctx.moveTo(-18, -18); ctx.quadraticCurveTo(-34, -8 + Math.sin(t) * 3, -30, 6); ctx.stroke();
    ctx.restore();
  }

  function drawMara(ctx, x, y, s, t) {
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
    ctx.fillStyle = '#7a4a8a'; ctx.beginPath(); ctx.ellipse(0, -30, 26, 30, 0, 0, 7); ctx.fill();
    ctx.fillStyle = '#e8d8c0'; ctx.beginPath(); ctx.ellipse(0, -22, 15, 17, 0, 0, 7); ctx.fill();
    ctx.fillStyle = '#c9a06a'; ctx.beginPath(); ctx.arc(0, -66, 13, 0, 7); ctx.fill();
    ctx.fillStyle = '#4a2a1a'; ctx.beginPath(); ctx.arc(0, -70, 13, Math.PI, 0); ctx.fill();
    ctx.strokeStyle = '#3a2a1a'; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(14, -34); ctx.lineTo(30, -52); ctx.stroke();
    ctx.fillStyle = '#f2c14e'; ctx.beginPath(); ctx.arc(32, -56, 6, 0, 7); ctx.fill();
    ctx.fillStyle = '#fff3b0'; ctx.beginPath(); ctx.arc(32, -56, 3, 0, 7); ctx.fill();
    ctx.restore();
  }

  function drawOldFen(ctx, x, y, s, t) {
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
    ctx.fillStyle = '#3a3a44'; ctx.beginPath(); ctx.ellipse(0, -26, 20, 24, 0.15, 0, 7); ctx.fill();
    ctx.fillStyle = '#c9b8a0'; ctx.beginPath(); ctx.arc(4, -56, 11, 0, 7); ctx.fill();
    ctx.fillStyle = '#4a6a2a'; ctx.beginPath(); ctx.ellipse(4, -46, 9, 8, 0, 0, 7); ctx.fill();
    ctx.strokeStyle = '#3a3a44'; ctx.lineWidth = 4; ctx.beginPath(); ctx.moveTo(-8, -20); ctx.lineTo(-16, 0); ctx.moveTo(10, -20); ctx.lineTo(18, 0); ctx.stroke();
    ctx.strokeStyle = '#c9a227'; ctx.lineWidth = 2.4; ctx.beginPath(); ctx.moveTo(16, -30); ctx.lineTo(26, -22); ctx.stroke();
    ctx.beginPath(); ctx.arc(28, -20, 3.4, 0, 7); ctx.stroke();
    ctx.restore();
  }

  function drawMoon(ctx, x, y, s, t) {
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
    ctx.fillStyle = '#f4ecd8';
    ctx.beginPath(); ctx.arc(0, -70, 34, 0, 7); ctx.fill();
    ctx.fillStyle = '#1c2438';
    ctx.beginPath(); ctx.arc(12, -74, 30, 0, 7); ctx.fill();
    ctx.fillStyle = '#f4ecd8';
    ctx.beginPath(); ctx.arc(-6, -70, 3, 0, 7); ctx.arc(-16, -70, 3, 0, 7); ctx.fill();
    ctx.strokeStyle = '#8a7a5a'; ctx.lineWidth = 1.6; ctx.beginPath(); ctx.arc(-11, -62, 4, 0.1 * Math.PI, 0.9 * Math.PI); ctx.stroke();
    ctx.restore();
  }

  function drawActor(ctx, id, x, y, s, t) {
    if (id === 'char_pip') drawPip(ctx, x, y, s, t);
    else if (id === 'char_mara') drawMara(ctx, x, y, s, t);
    else if (id === 'char_old_fen') drawOldFen(ctx, x, y, s, t);
    else if (id === 'char_moon') drawMoon(ctx, x, y, s, t);
  }

  function drawScene(canvas, scene, cast) {
    var ctx = canvas.getContext('2d');
    var W = canvas.width, H = canvas.height;
    var art = INKY_ART[scene.id] || ['#222', '#333', '#fff', 50, 50, 100, 'village gathering', []];
    var sky = art[0], ground = art[1], light = art[2], px = art[3], py = art[4], sc = art[5] / 100 * 1.5;
    var landmark = art[6], actors = art[7] || [];
    var t = performance.now() / 1000;

    var grad = ctx.createLinearGradient(0, 0, 0, H);
    grad.addColorStop(0, sky); grad.addColorStop(1, shade(sky, -18));
    ctx.fillStyle = grad; ctx.fillRect(0, 0, W, H);

    var glow = ctx.createRadialGradient(W * px / 100, H * py / 100, 4, W * px / 100, H * py / 100, H * 0.55);
    glow.addColorStop(0, light); glow.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.globalAlpha = 0.55; ctx.fillStyle = glow; ctx.fillRect(0, 0, W, H); ctx.globalAlpha = 1;

    ctx.fillStyle = ground; ctx.fillRect(0, H * 0.72, W, H * 0.28);
    ctx.fillStyle = shade(ground, -22); ctx.fillRect(0, H * 0.72, W, 6);

    drawLandmark(ctx, landmark, W, H, sc);

    var n = actors.length;
    for (var i = 0; i < n; i++) {
      var ax = W * (0.28 + 0.44 * (n === 1 ? 0.5 : i / (n - 1)));
      var ay = H * 0.78;
      drawActor(ctx, actors[i], ax, ay, sc * 0.9, t + i);
    }
  }

  function shade(hex, amt) {
    var n = parseInt(hex.slice(1), 16);
    var r = Math.max(0, Math.min(255, (n >> 16) + amt));
    var g = Math.max(0, Math.min(255, ((n >> 8) & 255) + amt));
    var b = Math.max(0, Math.min(255, (n & 255) + amt));
    return 'rgb(' + r + ',' + g + ',' + b + ')';
  }

  window.drawScene = drawScene;
  var INKY_ART = window.INKY_ART;
})();
