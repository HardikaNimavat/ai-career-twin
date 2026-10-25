/**
 * AI Career Twin — Dynamic Role-Specific Constellation Knowledge Graph
 * 
 * Crystal-clear single-orbit layout with zero text overlaps, radial quadrant labels,
 * and clean external legend header.
 */

const CLUSTER_COLORS = {
  frontend: "#00E8A8",  // Emerald
  backend: "#5EA8FF",   // Sapphire Blue
  data: "#FFB648",      // Amber / Gold
  devops: "#FF6B7A",    // Coral Red
  database: "#C792EA",  // Purple
  mobile: "#5EE6E6",    // Cyan
  general: "#94A3B8"    // Slate
};

const CLUSTER_LABELS = {
  frontend: "Frontend & UI",
  backend: "Backend & Systems",
  data: "Data & ML",
  devops: "Cloud & DevOps",
  database: "Databases & Storage",
  mobile: "Mobile Architecture",
  general: "Core Engineering"
};

const ROLE_TAXONOMY_MAP = {
  data: {
    label: "Data Scientist",
    cluster: "data",
    color: "#FFB648",
    description: "Machine Learning, Statistics & Data Engineering",
    coreSkills: [
      { name: "Python", weight: 3, cluster: "backend" },
      { name: "Machine Learning", weight: 3, cluster: "data" },
      { name: "Pandas", weight: 3, cluster: "data" },
      { name: "NumPy", weight: 2, cluster: "data" },
      { name: "Statistics", weight: 3, cluster: "data" },
      { name: "SQL", weight: 2, cluster: "database" },
      { name: "Data Visualization", weight: 2, cluster: "data" },
      { name: "Deep Learning", weight: 1, cluster: "data" }
    ],
    bridges: [
      { from: "Python", to: "Pandas" },
      { from: "Python", to: "NumPy" },
      { from: "Python", to: "Machine Learning" },
      { from: "Machine Learning", to: "Deep Learning" },
      { from: "Problem Solving", to: "Statistics" },
      { from: "HTML/CSS", to: "Data Visualization" }
    ]
  },
  backend: {
    label: "Backend Developer",
    cluster: "backend",
    color: "#5EA8FF",
    description: "Distributed Systems, Microservices & High-Throughput APIs",
    coreSkills: [
      { name: "Node.js", weight: 3, cluster: "backend" },
      { name: "Express.js", weight: 2, cluster: "backend" },
      { name: "REST APIs", weight: 3, cluster: "backend" },
      { name: "PostgreSQL", weight: 2, cluster: "database" },
      { name: "SQL", weight: 2, cluster: "database" },
      { name: "Docker", weight: 2, cluster: "devops" },
      { name: "System Design", weight: 2, cluster: "general" },
      { name: "Git", weight: 1, cluster: "devops" }
    ],
    bridges: [
      { from: "JavaScript", to: "Node.js" },
      { from: "Node.js", to: "Express.js" },
      { from: "Node.js", to: "REST APIs" },
      { from: "Python", to: "REST APIs" },
      { from: "PostgreSQL", to: "SQL" },
      { from: "REST APIs", to: "System Design" },
      { from: "Git", to: "Docker" }
    ]
  },
  frontend: {
    label: "Frontend Developer",
    cluster: "frontend",
    color: "#00E8A8",
    description: "Modern Client-Side Architecture, Component Trees & UX",
    coreSkills: [
      { name: "React", weight: 3, cluster: "frontend" },
      { name: "JavaScript", weight: 3, cluster: "frontend" },
      { name: "TypeScript", weight: 2, cluster: "frontend" },
      { name: "HTML/CSS", weight: 3, cluster: "frontend" },
      { name: "Tailwind CSS", weight: 2, cluster: "frontend" },
      { name: "Next.js", weight: 2, cluster: "frontend" },
      { name: "Redux", weight: 1, cluster: "frontend" },
      { name: "Testing", weight: 1, cluster: "general" },
      { name: "Git", weight: 1, cluster: "devops" }
    ],
    bridges: [
      { from: "HTML/CSS", to: "Tailwind CSS" },
      { from: "JavaScript", to: "React" },
      { from: "JavaScript", to: "TypeScript" },
      { from: "React", to: "Next.js" },
      { from: "React", to: "Redux" },
      { from: "JavaScript", to: "Testing" }
    ]
  },
  devops: {
    label: "DevOps Engineer",
    cluster: "devops",
    color: "#FF6B7A",
    description: "Containerization, Cloud Infrastructure & Automated CI/CD",
    coreSkills: [
      { name: "Docker", weight: 3, cluster: "devops" },
      { name: "Kubernetes", weight: 3, cluster: "devops" },
      { name: "AWS", weight: 3, cluster: "devops" },
      { name: "CI/CD", weight: 3, cluster: "devops" },
      { name: "Terraform", weight: 2, cluster: "devops" },
      { name: "Linux", weight: 2, cluster: "devops" },
      { name: "Git", weight: 1, cluster: "devops" }
    ],
    bridges: [
      { from: "Git", to: "CI/CD" },
      { from: "CI/CD", to: "Docker" },
      { from: "Docker", to: "Kubernetes" },
      { from: "Linux", to: "AWS" },
      { from: "Docker", to: "Terraform" }
    ]
  },
  fullstack: {
    label: "Full Stack Developer",
    cluster: "database",
    color: "#C792EA",
    description: "End-to-End Web Systems, Reactive Frontends & Microservices",
    coreSkills: [
      { name: "React", weight: 2, cluster: "frontend" },
      { name: "Node.js", weight: 2, cluster: "backend" },
      { name: "JavaScript", weight: 2, cluster: "frontend" },
      { name: "REST APIs", weight: 2, cluster: "backend" },
      { name: "MongoDB", weight: 2, cluster: "database" },
      { name: "SQL", weight: 1, cluster: "database" },
      { name: "Git", weight: 1, cluster: "devops" },
      { name: "System Design", weight: 1, cluster: "general" },
      { name: "Docker", weight: 1, cluster: "devops" }
    ],
    bridges: [
      { from: "HTML/CSS", to: "React" },
      { from: "JavaScript", to: "Node.js" },
      { from: "Node.js", to: "REST APIs" },
      { from: "REST APIs", to: "MongoDB" },
      { from: "Git", to: "Docker" }
    ]
  },
  mobile: {
    label: "Mobile Developer",
    cluster: "mobile",
    color: "#5EE6E6",
    description: "Cross-Platform Mobile Apps, Native SDKs & Reactive UI",
    coreSkills: [
      { name: "React Native", weight: 2, cluster: "mobile" },
      { name: "Flutter", weight: 2, cluster: "mobile" },
      { name: "Swift", weight: 2, cluster: "mobile" },
      { name: "Kotlin", weight: 2, cluster: "mobile" },
      { name: "Android SDK", weight: 3, cluster: "mobile" },
      { name: "Git", weight: 1, cluster: "devops" }
    ],
    bridges: [
      { from: "JavaScript", to: "React Native" },
      { from: "Git", to: "Android SDK" },
      { from: "React Native", to: "Flutter" }
    ]
  }
};

const SKILL_MAP = {
  "React":"frontend","Vue.js":"frontend","Angular":"frontend","JavaScript":"frontend","TypeScript":"frontend",
  "HTML/CSS":"frontend","Tailwind CSS":"frontend","Next.js":"frontend","Redux":"frontend","Webpack":"frontend",
  "Node.js":"backend","Express.js":"backend","Django":"backend","Flask":"backend","Spring Boot":"backend",
  "REST APIs":"backend","GraphQL":"backend","Java":"backend","Python":"backend","PHP":"backend","Ruby on Rails":"backend",
  "Machine Learning":"data","Deep Learning":"data","Pandas":"data","NumPy":"data","TensorFlow":"data","PyTorch":"data",
  "Data Visualization":"data","SQL":"data","R":"data","Statistics":"data","scikit-learn":"data",
  "Docker":"devops","Kubernetes":"devops","AWS":"devops","CI/CD":"devops","Terraform":"devops","Jenkins":"devops",
  "Linux":"devops","Git":"devops","Azure":"devops",
  "MongoDB":"database","PostgreSQL":"database","MySQL":"database","Redis":"database","Firebase":"database","SQLite":"database",
  "React Native":"mobile","Flutter":"mobile","Swift":"mobile","Kotlin":"mobile","Android SDK":"mobile","iOS Development":"mobile",
  "Communication":"general","Problem Solving":"general","Agile/Scrum":"general","System Design":"general",
  "Testing":"general","Data Structures & Algorithms":"general"
};

/**
 * Renders an interactive, role-distinct Digital Twin Constellation graph with zero overlaps
 */
function renderConstellation(detectedSkills = {}, targetRole = "frontend", gapRows = [], readiness = 0) {
  const svg = document.getElementById('constellationSvg');
  if (!svg) return;

  const roleKey = (targetRole || "frontend").toLowerCase();
  const roleConfig = ROLE_TAXONOMY_MAP[roleKey] || ROLE_TAXONOMY_MAP["frontend"];
  const targetColor = roleConfig.color;

  // ViewBox Geometry: 760 x 500
  const cx = 380, cy = 250;
  const ORBIT_R = 155;

  // Gap lookup
  const gapMap = {};
  if (gapRows && Array.isArray(gapRows)) {
    gapRows.forEach(r => {
      gapMap[r.skill] = r;
    });
  }

  // Build unified nodes array
  const nodeMap = new Map();

  // 1. Add Target Role Requirements
  roleConfig.coreSkills.forEach((item, idx) => {
    const isDirectHit = detectedSkills.hasOwnProperty(item.name) && (detectedSkills[item.name] >= 50);
    const gapInfo = gapMap[item.name] || {};
    const matchPct = isDirectHit ? (detectedSkills[item.name] || 100) : (gapInfo.match_pct || 0);
    const badgeStatus = isDirectHit ? "mastered" : (matchPct >= 30 ? "bridge" : "gap");

    nodeMap.set(item.name, {
      name: item.name,
      cluster: item.cluster || SKILL_MAP[item.name] || "general",
      isTargetReq: true,
      isDirectHit: isDirectHit,
      matchPct: matchPct,
      badgeStatus: badgeStatus,
      weight: item.weight,
      order: idx
    });
  });

  // 2. Add Candidate extra detected skills (Foundational assets)
  Object.entries(detectedSkills).forEach(([skillName, conf], idx) => {
    if (!nodeMap.has(skillName)) {
      nodeMap.set(skillName, {
        name: skillName,
        cluster: SKILL_MAP[skillName] || "general",
        isTargetReq: false,
        isDirectHit: true,
        matchPct: conf,
        badgeStatus: "mastered",
        weight: 1,
        order: 100 + idx
      });
    }
  });

  const nodes = Array.from(nodeMap.values());
  const N = nodes.length;

  // Single spacious orbit layout with optimal angular distribution
  const positions = {};
  nodes.forEach((node, i) => {
    // Start top (-PI/2) and spread clockwise
    const angle = (i / Math.max(N, 1)) * Math.PI * 2 - Math.PI / 2;
    positions[node.name] = {
      x: cx + Math.cos(angle) * ORBIT_R,
      y: cy + Math.sin(angle) * ORBIT_R,
      angle: angle,
      node: node
    };
  });

  let svgParts = [];

  // 1. Defs & Gradients
  svgParts.push(`
    <defs>
      <radialGradient id="centerGlow" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stop-color="${targetColor}" stop-opacity="0.22"/>
        <stop offset="65%" stop-color="${targetColor}" stop-opacity="0.05"/>
        <stop offset="100%" stop-color="${targetColor}" stop-opacity="0.00"/>
      </radialGradient>
      <filter id="nodeGlow" x="-20%" y="-20%" width="140%" height="140%">
        <feGaussianBlur stdDeviation="2.5" result="blur"/>
        <feComposite in="SourceGraphic" in2="blur" operator="over"/>
      </filter>
    </defs>
  `);

  // Background Ambience Cloud
  svgParts.push(`<circle cx="${cx}" cy="${cy}" r="${ORBIT_R + 50}" fill="url(#centerGlow)"/>`);

  // Orbital Guide Ring (Subtle Dashed)
  svgParts.push(`<circle cx="${cx}" cy="${cy}" r="${ORBIT_R}" fill="none" stroke="rgba(255,255,255,0.08)" stroke-dasharray="6 6"/>`);

  // 2. Render Synergy & Prerequisite Bridges
  roleConfig.bridges.forEach(b => {
    const p1 = positions[b.from];
    const p2 = positions[b.to];
    if (p1 && p2) {
      svgParts.push(`
        <line x1="${p1.x}" y1="${p1.y}" x2="${p2.x}" y2="${p2.y}" 
              stroke="${targetColor}" stroke-opacity="0.40" stroke-width="1.6" stroke-dasharray="4 3"/>
      `);
    }
  });

  // 3. Render Radiating Center Lines (Center -> All Nodes)
  nodes.forEach(node => {
    const pos = positions[node.name];
    if (!pos) return;
    let strokeColor = "#FF5A6E";
    let strokeWidth = 1.0;
    let strokeOpacity = 0.25;
    let dash = `stroke-dasharray="2 4"`;

    if (node.badgeStatus === "mastered") {
      strokeColor = "#00E8A8";
      strokeWidth = 1.8;
      strokeOpacity = 0.60;
      dash = "";
    } else if (node.badgeStatus === "bridge") {
      strokeColor = "#FFB648";
      strokeWidth = 1.4;
      strokeOpacity = 0.45;
      dash = `stroke-dasharray="4 3"`;
    }

    svgParts.push(`
      <line x1="${cx}" y1="${cy}" x2="${pos.x}" y2="${pos.y}" 
            stroke="${strokeColor}" stroke-opacity="${strokeOpacity}" stroke-width="${strokeWidth}" ${dash}/>
    `);
  });

  // 4. Render Central Candidate Node (YOU)
  const readPct = Math.round(readiness || (window.STATE && window.STATE.gapAnalysis ? window.STATE.gapAnalysis.readiness : 20));
  
  svgParts.push(`<circle cx="${cx}" cy="${cy}" r="40" fill="none" stroke="${targetColor}" stroke-width="1.5" stroke-opacity="0.35" stroke-dasharray="4 3"/>`);
  svgParts.push(`<circle cx="${cx}" cy="${cy}" r="34" fill="#0C1018" stroke="${targetColor}" stroke-width="2.5" filter="url(#nodeGlow)"/>`);
  
  svgParts.push(`<text x="${cx}" y="${cy - 8}" text-anchor="middle" font-family="'Space Grotesk', sans-serif" font-size="12" fill="#FFFFFF" font-weight="700" letter-spacing="0.5">YOU</text>`);
  svgParts.push(`<text x="${cx}" y="${cy + 5}" text-anchor="middle" font-family="'Inter', sans-serif" font-size="8.5" fill="${targetColor}" font-weight="700" letter-spacing="0.8">${roleKey.toUpperCase()}</text>`);
  svgParts.push(`<text x="${cx}" y="${cy + 17}" text-anchor="middle" font-family="'JetBrains Mono', monospace" font-size="9" fill="#94A3B8" font-weight="600">${readPct}% Ready</text>`);

  // 5. Render Nodes & Non-Overlapping Radial Outward Labels
  nodes.forEach(node => {
    const pos = positions[node.name];
    if (!pos) return;

    const isMastered = node.badgeStatus === "mastered";
    const isBridge = node.badgeStatus === "bridge";
    const isGap = node.badgeStatus === "gap";
    const nodeR = isMastered ? 12 : (isBridge ? 10 : 8.5);

    // Node Circle
    if (isMastered) {
      svgParts.push(`<circle cx="${pos.x}" cy="${pos.y}" r="${nodeR + 4}" fill="none" stroke="#00E8A8" stroke-opacity="0.35" stroke-width="2"/>`);
      svgParts.push(`<circle cx="${pos.x}" cy="${pos.y}" r="${nodeR}" fill="#00E8A8" stroke="#FFFFFF" stroke-width="1.5"/>`);
      svgParts.push(`<text x="${pos.x}" y="${pos.y + 3.5}" text-anchor="middle" font-family="'Inter', sans-serif" font-size="9.5" fill="#04140F" font-weight="800">✓</text>`);
    } else if (isBridge) {
      svgParts.push(`<circle cx="${pos.x}" cy="${pos.y}" r="${nodeR + 4}" fill="none" stroke="#FFB648" stroke-dasharray="3 2" stroke-opacity="0.5" stroke-width="1.5"/>`);
      svgParts.push(`<circle cx="${pos.x}" cy="${pos.y}" r="${nodeR}" fill="#1E1910" stroke="#FFB648" stroke-width="2"/>`);
      svgParts.push(`<text x="${pos.x}" y="${pos.y + 3.5}" text-anchor="middle" font-family="'JetBrains Mono', monospace" font-size="8" fill="#FFB648" font-weight="700">~</text>`);
    } else {
      svgParts.push(`<circle cx="${pos.x}" cy="${pos.y}" r="${nodeR + 3}" fill="none" stroke="#FF5A6E" stroke-dasharray="2 3" stroke-opacity="0.4" stroke-width="1.2"/>`);
      svgParts.push(`<circle cx="${pos.x}" cy="${pos.y}" r="${nodeR}" fill="#191114" stroke="#FF5A6E" stroke-width="1.5"/>`);
      svgParts.push(`<text x="${pos.x}" y="${pos.y + 3}" text-anchor="middle" font-family="'Inter', sans-serif" font-size="7.5" fill="#FF5A6E" font-weight="700">✕</text>`);
    }

    // Status label text
    const statusText = isMastered 
      ? `${Math.round(node.matchPct)}% Confirmed` 
      : (isBridge ? `${Math.round(node.matchPct)}% Transferable` : `Target Gap (w${node.weight})`);
    
    const statusFill = isMastered ? "#00E8A8" : (isBridge ? "#FFB648" : "#FF5A6E");

    // Quadrant-aware radial label positioning
    const cosA = Math.cos(pos.angle);
    const sinA = Math.sin(pos.angle);

    let textAnchor = "middle";
    let pillX = 0;
    let pillY = 0;
    let labelX = pos.x;
    let line1Y = 0;
    let line2Y = 0;

    const pillW = Math.max(node.name.length * 7.5, statusText.length * 6.4) + 14;
    const pillH = 26;

    if (cosA > 0.35) {
      // Right quadrant: Label starts to the right of node
      textAnchor = "start";
      labelX = pos.x + nodeR + 8;
      pillX = pos.x + nodeR + 3;
      pillY = pos.y - pillH / 2;
      line1Y = pos.y - 2;
      line2Y = pos.y + 9;
    } else if (cosA < -0.35) {
      // Left quadrant: Label ends to the left of node
      textAnchor = "end";
      labelX = pos.x - nodeR - 8;
      pillX = pos.x - nodeR - pillW - 3;
      pillY = pos.y - pillH / 2;
      line1Y = pos.y - 2;
      line2Y = pos.y + 9;
    } else if (sinA < 0) {
      // Top sector: Label sits cleanly above node
      textAnchor = "middle";
      labelX = pos.x;
      pillX = pos.x - pillW / 2;
      pillY = pos.y - nodeR - pillH - 4;
      line1Y = pillY + 10;
      line2Y = pillY + 21;
    } else {
      // Bottom sector: Label sits cleanly below node
      textAnchor = "middle";
      labelX = pos.x;
      pillX = pos.x - pillW / 2;
      pillY = pos.y + nodeR + 6;
      line1Y = pillY + 11;
      line2Y = pillY + 22;
    }

    svgParts.push(`
      <rect x="${pillX}" y="${pillY}" width="${pillW}" height="${pillH}" rx="5" 
            fill="rgba(8, 12, 18, 0.90)" stroke="rgba(255, 255, 255, 0.10)" stroke-width="1"/>
      <text x="${labelX}" y="${line1Y}" text-anchor="${textAnchor}" font-family="'Inter', sans-serif" font-size="10.5" fill="#EEF2F7" font-weight="600">
        ${node.name}
      </text>
      <text x="${labelX}" y="${line2Y}" text-anchor="${textAnchor}" font-family="'JetBrains Mono', monospace" font-size="8" fill="${statusFill}" font-weight="600">
        ${statusText}
      </text>
    `);
  });

  svg.innerHTML = svgParts.join("");

  // 6. Update Header Title & Legend Strip
  const titleBadge = document.getElementById('constellationTitleBadge');
  if (titleBadge) {
    titleBadge.textContent = `✦ ${roleConfig.label.toUpperCase()} ECOSYSTEM ✦`;
    titleBadge.style.color = targetColor;
  }

  const legend = document.getElementById('constellationLegend');
  if (legend) {
    const masteredCount = nodes.filter(n => n.badgeStatus === "mastered").length;
    const bridgeCount = nodes.filter(n => n.badgeStatus === "bridge").length;
    const gapCount = nodes.filter(n => n.badgeStatus === "gap").length;

    legend.innerHTML = `
      <div class="constellation-legend-item">
        <span class="legend-dot" style="background:#00E8A8; box-shadow:0 0 6px #00E8A8;"></span>
        <span>Mastered (${masteredCount})</span>
      </div>
      <div class="constellation-legend-item">
        <span class="legend-dot" style="background:#FFB648; box-shadow:0 0 6px #FFB648;"></span>
        <span>Bridge (${bridgeCount})</span>
      </div>
      <div class="constellation-legend-item">
        <span class="legend-dot" style="background:#FF5A6E; box-shadow:0 0 6px #FF5A6E;"></span>
        <span>Gap (${gapCount})</span>
      </div>
    `;
  }

  // 7. Update Constellation Summary Bar
  const summaryBar = document.getElementById('constellationSummaryBar');
  if (summaryBar) {
    const totalRequired = roleConfig.coreSkills.length;
    const masteredInRole = roleConfig.coreSkills.filter(s => detectedSkills.hasOwnProperty(s.name) && detectedSkills[s.name] >= 50).length;
    const directCoverage = Math.round((masteredInRole / totalRequired) * 100);

    summaryBar.innerHTML = `
      <div class="constellation-metric-pill">
        <span class="pill-label">Target Role</span>
        <span class="pill-val" style="color:${targetColor}">${roleConfig.label}</span>
      </div>
      <div class="constellation-metric-pill">
        <span class="pill-label">Overall Readiness</span>
        <span class="pill-val" style="color:${readPct >= 45 ? '#00E8A8' : '#FFB648'}">${readPct}%</span>
      </div>
      <div class="constellation-metric-pill">
        <span class="pill-label">Role Skills Met</span>
        <span class="pill-val">${masteredInRole} / ${totalRequired} (${directCoverage}%)</span>
      </div>
      <div class="constellation-metric-pill">
        <span class="pill-label">Dominant Cluster</span>
        <span class="pill-val" style="color:#5EA8FF">${CLUSTER_LABELS[roleConfig.cluster] || 'Technology'}</span>
      </div>
    `;
  }
}
