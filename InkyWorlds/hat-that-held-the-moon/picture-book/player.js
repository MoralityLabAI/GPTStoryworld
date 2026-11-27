/* player.js — interaction layer for The Hat That Held the Moon */
(function () {
  'use strict';

  var WORLD = window.WORLD;
  if (!WORLD || !WORLD.scenes) {
    console.error('world-data.js did not provide window.WORLD');
    return;
  }

  var sceneIndex = 0;
  var stats = JSON.parse(JSON.stringify(WORLD.stats));
  var currentReactionId = null;
  var currentEndingId = null;
  var awaitingContinue = false;

  var sceneTitle = document.getElementById('scene-title');
  var sceneText = document.getElementById('scene-text');
  var choicesEl = document.getElementById('choices');
  var reactionEl = document.getElementById('reaction');
  var continueBtn = document.getElementById('continue');
  var restartBtn = document.getElementById('restart');
  var canvas = document.getElementById('art');

  var trustVal = document.getElementById('trust-val');
  var nerveVal = document.getElementById('nerve-val');
  var careVal = document.getElementById('care-val');
  var trustBar = document.getElementById('trust-bar');
  var nerveBar = document.getElementById('nerve-bar');
  var careBar = document.getElementById('care-bar');
  var castList = document.getElementById('cast-list');

  function clamp(v) {
    if (v < -1) return -1;
    if (v > 1) return 1;
    return v;
  }

  function currentScene() {
    return WORLD.scenes[sceneIndex];
  }

  function isTerminal(scene) {
    return !!(scene.ending || (scene.id && /^end_/.test(scene.id)));
  }

  function renderMeters() {
    trustVal.textContent = stats.trust.toFixed(2);
    nerveVal.textContent = stats.nerve.toFixed(2);
    careVal.textContent = stats.care.toFixed(2);
    // Map [-1, 1] to [0, 100] for display
    trustBar.style.width = (((stats.trust + 1) / 2) * 100).toFixed(1) + '%';
    nerveBar.style.width = (((stats.nerve + 1) / 2) * 100).toFixed(1) + '%';
    careBar.style.width = (((stats.care + 1) / 2) * 100).toFixed(1) + '%';
  }

  function renderCast() {
    if (!castList) return;
    castList.innerHTML = '';
    (WORLD.cast || []).forEach(function (member) {
      var li = document.createElement('li');
      var dot = document.createElement('span');
      dot.className = 'dot';
      dot.style.background = member.visual || '#888';
      var body = document.createElement('span');
      var name = document.createElement('span');
      name.className = 'name';
      name.textContent = member.name || member.id || 'Unknown';
      var voice = document.createElement('span');
      voice.className = 'voice';
      voice.textContent = member.voice ? ' — ' + member.voice : '';
      var visual = document.createElement('div');
      visual.className = 'visual';
      visual.textContent = member.visual || '';
      body.appendChild(name);
      body.appendChild(voice);
      body.appendChild(visual);
      li.appendChild(dot);
      li.appendChild(body);
      castList.appendChild(li);
    });
  }

  function renderScene() {
    var scene = currentScene();
    sceneTitle.textContent = scene.title || scene.id || 'Untitled scene';
    sceneText.textContent = scene.text || '';
    reactionEl.textContent = '';
    currentReactionId = null;
    currentEndingId = isTerminal(scene) ? scene.id : null;
    awaitingContinue = false;

    // Clear choices
    choicesEl.innerHTML = '';
    var terminal = isTerminal(scene);
    if (!terminal && scene.options && scene.options.length) {
      scene.options.forEach(function (opt, idx) {
        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'choice-btn';
        btn.setAttribute('data-option', opt.id);
        var key = document.createElement('span');
        key.className = 'key';
        key.textContent = String.fromCharCode(65 + idx);
        var label = document.createElement('span');
        label.textContent = opt.text || '';
        btn.appendChild(key);
        btn.appendChild(label);
        btn.addEventListener('click', function () {
          chooseOption(opt);
        });
        choicesEl.appendChild(btn);
      });
    }

    continueBtn.disabled = true;
    continueBtn.textContent = 'Continue →';

    if (window.drawScene) {
      try {
        window.drawScene(canvas, scene, WORLD.cast);
      } catch (err) {
        console.error('drawScene failed:', err);
      }
    }
    renderMeters();
  }

  function chooseOption(opt) {
    var reactions = opt.reactions || [];
    if (!reactions.length) {
      reactionEl.textContent = 'Nothing answers.';
      return;
    }
    var best = null;
    var bestScore = -Infinity;
    for (var i = 0; i < reactions.length; i++) {
      var r = reactions[i];
var computed = r.score[0] * 1 + r.score[1] * stats.trust + r.score[2] * stats.nerve + r.score[3] * stats.care;
      if (computed > bestScore) {
        bestScore = computed;
        best = r;
      }
    }
    if (!best) return;

    currentReactionId = best.id || null;
    var effects = best.effects || {};
    Object.keys(effects).forEach(function (key) {
      var delta = Number(effects[key]);
      if (!isFinite(delta)) return;
      if (key === 'trust') stats.trust = clamp(stats.trust + delta);
      else if (key === 'nerve') stats.nerve = clamp(stats.nerve + delta);
      else if (key === 'care') stats.care = clamp(stats.care + delta);
    });

    reactionEl.textContent = best.text || '';

    // Disable choice buttons after selection
    var btns = choicesEl.querySelectorAll('button[data-option]');
    for (var j = 0; j < btns.length; j++) btns[j].disabled = true;

    continueBtn.disabled = false;
    continueBtn.textContent = 'Continue →';
    awaitingContinue = true;
    renderMeters();
  }

  continueBtn.addEventListener('click', function () {
    if (!awaitingContinue) return;
    var scene = currentScene();
    // Find the reaction we chose to know its .to target.
    // We stored only the id; recompute by scanning options.
    var target = null;
    var options = scene.options || [];
    for (var i = 0; i < options.length; i++) {
      var reactions = options[i].reactions || [];
      for (var j = 0; j < reactions.length; j++) {
        if (reactions[j].id === currentReactionId) {
          target = reactions[j].to;
          break;
        }
      }
      if (target) break;
    }
    if (!target) {
      // Fallback: advance to next scene if possible
      if (sceneIndex < WORLD.scenes.length - 1) {
        sceneIndex += 1;
      }
    } else {
      var found = -1;
      for (var k = 0; k < WORLD.scenes.length; k++) {
        if (WORLD.scenes[k].id === target) { found = k; break; }
      }
      if (found >= 0) sceneIndex = found;
    }
    renderScene();
  });

  restartBtn.addEventListener('click', function () {
    sceneIndex = 0;
    stats = JSON.parse(JSON.stringify(WORLD.stats));
    currentReactionId = null;
    currentEndingId = null;
    awaitingContinue = false;
    renderScene();
  });

  window.gameState = function () {
    return {
      scene: currentScene().id,
      stats: { trust: stats.trust, nerve: stats.nerve, care: stats.care },
      reaction: currentReactionId,
      ending: currentEndingId
    };
  };

  renderCast();
  renderScene();
})();
