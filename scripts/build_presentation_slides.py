import os
import subprocess
from PIL import Image

OUTPUT_DIR = r"C:\Users\Hp\OneDrive\Desktop\RAG ChatBot\docs\carousel"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1080x1350 4:5 Vertical Carousel — Executive Tech Keynote Design
# No dead space, perfectly balanced vertical rhythm, mobile-first large typography
CSS_COMMON = """
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    width: 1080px;
    height: 1350px;
    background: #070A12;
    background-image: 
      radial-gradient(circle at 85% 10%, rgba(0, 229, 255, 0.20) 0%, transparent 45%),
      radial-gradient(circle at 10% 90%, rgba(16, 185, 129, 0.16) 0%, transparent 45%),
      radial-gradient(circle at 50% 50%, rgba(99, 102, 241, 0.08) 0%, transparent 60%);
    font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    color: #F8FAFC;
    padding: 65px 65px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    overflow: hidden;
    -webkit-font-smoothing: antialiased;
  }
  .mono { font-family: 'SF Mono', 'Consolas', 'Courier New', monospace; }

  /* Top Bar */
  .top-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 60px;
  }
  .brand {
    display: flex;
    align-items: center;
    gap: 16px;
  }
  .brand-icon {
    width: 52px;
    height: 52px;
    background: linear-gradient(135deg, rgba(0, 229, 255, 0.35), rgba(99, 102, 241, 0.3));
    border: 1.5px solid rgba(0, 229, 255, 0.6);
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 26px;
    box-shadow: 0 8px 24px rgba(0, 229, 255, 0.3);
  }
  .brand-tag {
    font-size: 13px;
    font-weight: 800;
    color: #38BDF8;
    letter-spacing: 0.14em;
    text-transform: uppercase;
  }
  .brand-title {
    font-size: 24px;
    font-weight: 900;
    color: #FFFFFF;
    letter-spacing: -0.02em;
  }
  .slide-counter {
    padding: 9px 22px;
    border-radius: 9999px;
    background: rgba(15, 23, 42, 0.95);
    border: 1.5px solid rgba(255, 255, 255, 0.18);
    color: #94A3B8;
    font-size: 16px;
    font-weight: 800;
    letter-spacing: 0.08em;
  }

  /* Pills */
  .pill-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 20px;
    border-radius: 9999px;
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    width: fit-content;
    margin-bottom: 12px;
  }
  .pill-cyan {
    background: rgba(0, 229, 255, 0.15);
    border: 1.5px solid rgba(0, 229, 255, 0.5);
    color: #38BDF8;
  }
  .pill-emerald {
    background: rgba(16, 185, 129, 0.15);
    border: 1.5px solid rgba(16, 185, 129, 0.5);
    color: #34D399;
  }
  .pill-coral {
    background: rgba(248, 113, 113, 0.15);
    border: 1.5px solid rgba(248, 113, 113, 0.5);
    color: #F87171;
  }

  /* Typography */
  h1 {
    font-size: 58px;
    font-weight: 900;
    line-height: 1.15;
    letter-spacing: -0.035em;
    color: #FFFFFF;
    margin-bottom: 14px;
  }
  .gradient-cyan {
    background: linear-gradient(135deg, #00E5FF 0%, #38BDF8 60%, #818CF8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .gradient-emerald {
    background: linear-gradient(135deg, #34D399 0%, #10B981 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .gradient-coral {
    background: linear-gradient(135deg, #F87171 0%, #FB7185 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  p.lead-text {
    font-size: 22px;
    line-height: 1.5;
    color: #94A3B8;
    font-weight: 400;
  }

  /* Cards */
  .card-glow {
    background: linear-gradient(165deg, rgba(16, 26, 48, 0.95) 0%, rgba(9, 14, 28, 0.98) 100%);
    border: 1.5px solid rgba(0, 229, 255, 0.4);
    border-radius: 26px;
    box-shadow: 0 25px 60px rgba(0, 0, 0, 0.6), 0 0 35px rgba(0, 229, 255, 0.15);
  }

  /* Footer */
  .footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-top: 1.5px solid rgba(255, 255, 255, 0.12);
    padding-top: 24px;
    height: 60px;
    font-size: 17px;
    color: #64748B;
  }
  .footer-name {
    color: #94A3B8;
    font-weight: 600;
  }
  .footer-name strong {
    color: #FFFFFF;
    font-weight: 800;
  }
  .footer-action {
    color: #38BDF8;
    font-weight: 800;
    font-size: 18px;
    display: flex;
    align-items: center;
    gap: 8px;
  }
"""

slides_html = {}

# -------------------------------------------------------------
# SLIDE 1: THE COVER (Hero Hook & Live App Reveal)
# -------------------------------------------------------------
slides_html["slide1"] = f"""<!DOCTYPE html>
<html>
<head><style>{CSS_COMMON}</style></head>
<body>
  <div class="top-bar">
    <div class="brand">
      <div class="brand-icon">🩺</div>
      <div>
        <div class="brand-tag">Production AI Case Study</div>
        <div class="brand-title">ClinicDocs AI</div>
      </div>
    </div>
    <div class="slide-counter mono">01 / 05</div>
  </div>

  <div style="flex: 1; display: flex; flex-direction: column; justify-content: space-evenly; padding: 10px 0;">
    <div>
      <div class="pill-badge pill-cyan">Healthcare Conversational RAG</div>
      <h1>Why 90% of RAG bots fail in production — <span class="gradient-cyan">and how I built one that doesn't.</span></h1>
      <p class="lead-text">Most tutorials crash under tight server memory, leak patient files across sessions, and hallucinate under trick queries. Here is how I engineered past every bottleneck.</p>
    </div>

    <!-- Realistic App Mockup Window -->
    <div class="card-glow" style="padding: 28px 32px;">
      <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1.5px solid rgba(255, 255, 255, 0.1); padding-bottom: 16px; margin-bottom: 20px;">
        <div style="display: flex; align-items: center; gap: 10px;">
          <span style="width: 14px; height: 14px; border-radius: 50%; background: #EF4444; display: inline-block;"></span>
          <span style="width: 14px; height: 14px; border-radius: 50%; background: #F59E0B; display: inline-block;"></span>
          <span style="width: 14px; height: 14px; border-radius: 50%; background: #10B981; display: inline-block;"></span>
          <span class="mono" style="font-size: 15px; color: #94A3B8; margin-left: 12px; font-weight: 600;">clinicdocs-ai.streamlit.app</span>
        </div>
        <span class="mono" style="font-size: 14px; background: rgba(16, 185, 129, 0.15); color: #34D399; padding: 6px 14px; border-radius: 8px; border: 1.5px solid rgba(16, 185, 129, 0.4); font-weight: 800;">✓ 10/10 EVALS PASSED</span>
      </div>

      <!-- User Query -->
      <div style="background: rgba(255, 255, 255, 0.04); border: 1.5px solid rgba(255, 255, 255, 0.1); border-radius: 16px; padding: 18px 24px; margin-bottom: 16px;">
        <div class="mono" style="font-size: 13px; color: #38BDF8; font-weight: 800; letter-spacing: 0.08em; margin-bottom: 6px;">PATIENT / USER QUERY:</div>
        <div style="font-size: 21px; color: #FFFFFF; font-weight: 700;">"What are the clinic operating hours on Friday?"</div>
      </div>

      <!-- Verified Grounded Answer -->
      <div style="background: rgba(7, 11, 20, 0.95); border: 1.5px solid rgba(0, 229, 255, 0.3); border-radius: 16px; padding: 22px 24px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
          <span class="mono" style="color: #2DD4BF; font-weight: 800; font-size: 15px;">🩺 CLINICDOCS AI (VERIFIED GROUNDED):</span>
          <span class="mono" style="color: #94A3B8; font-size: 14px; font-weight: 600;">⚡ 0.82s Latency</span>
        </div>
        <div style="font-size: 19px; color: #E2E8F0; line-height: 1.55; margin-bottom: 18px;">
          On Friday, Noor Care Clinic operates in two shifts:<br>
          <strong style="color: #FFFFFF;">• Morning:</strong> 9:00 AM – 1:00 PM<br>
          <strong style="color: #FFFFFF;">• Evening:</strong> 3:00 PM – 8:00 PM<br>
          <span style="color: #94A3B8; font-size: 17px;">(Clinic is closed between 1:00 PM and 3:00 PM for Friday prayers)</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1.5px solid rgba(255, 255, 255, 0.08); padding-top: 16px;">
          <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 18px;">📄</span>
            <span class="mono" style="font-size: 15px; color: #F8FAFC; font-weight: 700;">Noor_Care_Clinic_FAQ.pdf</span>
            <span class="mono" style="font-size: 14px; color: #34D399; font-weight: 900; background: rgba(16, 185, 129, 0.2); border: 1.5px solid rgba(16, 185, 129, 0.45); padding: 3px 12px; border-radius: 6px;">Page 1</span>
          </div>
          <span class="mono" style="font-size: 14px; color: #38BDF8; font-weight: 800; background: rgba(0, 229, 255, 0.15); padding: 4px 14px; border-radius: 6px;">Similarity: 78.2%</span>
        </div>
      </div>
    </div>

    <!-- 3 Big Metric Cards -->
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px;">
      <div style="background: rgba(13, 20, 36, 0.85); border: 1.5px solid rgba(0, 229, 255, 0.35); border-radius: 20px; padding: 24px 20px; text-align: center;">
        <div style="font-size: 42px; font-weight: 900; color: #38BDF8; font-family: 'SF Mono', monospace;">-70%</div>
        <div style="font-size: 16px; color: #F8FAFC; font-weight: 700; margin-top: 6px;">RAM Footprint</div>
        <div style="font-size: 13px; color: #94A3B8; margin-top: 2px;">Quantized ONNX Engine</div>
      </div>
      <div style="background: rgba(13, 20, 36, 0.85); border: 1.5px solid rgba(16, 185, 129, 0.35); border-radius: 20px; padding: 24px 20px; text-align: center;">
        <div style="font-size: 42px; font-weight: 900; color: #34D399; font-family: 'SF Mono', monospace;">&lt; 25ms</div>
        <div style="font-size: 16px; color: #F8FAFC; font-weight: 700; margin-top: 6px;">Refusal Gate</div>
        <div style="font-size: 13px; color: #94A3B8; margin-top: 2px;">Instant Vector Filter</div>
      </div>
      <div style="background: rgba(13, 20, 36, 0.85); border: 1.5px solid rgba(248, 113, 113, 0.35); border-radius: 20px; padding: 24px 20px; text-align: center;">
        <div style="font-size: 42px; font-weight: 900; color: #F87171; font-family: 'SF Mono', monospace;">$0.00</div>
        <div style="font-size: 16px; color: #F8FAFC; font-weight: 700; margin-top: 6px;">Off-Topic Cost</div>
        <div style="font-size: 13px; color: #94A3B8; margin-top: 2px;">0 Tokens Wasted</div>
      </div>
    </div>
  </div>

  <div class="footer">
    <div class="footer-name">Architected & Built by <strong>Farwa Ali Nasir</strong> • AI & ML Engineer</div>
    <div class="footer-action">Swipe for the breakdown →</div>
  </div>
</body>
</html>
"""

# -------------------------------------------------------------
# SLIDE 2: THE 3 PRODUCTION BOTTLENECKS (Balanced Vertical Space)
# -------------------------------------------------------------
slides_html["slide2"] = f"""<!DOCTYPE html>
<html>
<head><style>{CSS_COMMON}</style></head>
<body>
  <div class="top-bar">
    <div class="brand">
      <div class="brand-icon">⚡</div>
      <div>
        <div class="brand-tag">System Engineering</div>
        <div class="brand-title">The 3 Bottlenecks</div>
      </div>
    </div>
    <div class="slide-counter mono">02 / 05</div>
  </div>

  <div style="flex: 1; display: flex; flex-direction: column; justify-content: space-evenly; padding: 10px 0;">
    <div>
      <div class="pill-badge pill-coral">Why Tutorials Lie To You</div>
      <h1>Tutorial Demos vs <span class="gradient-emerald">Production Systems</span></h1>
      <p class="lead-text">Standard tutorial RAG breaks under strict container resource limits, multi-tenant isolation requirements, and off-topic questions. Here is how I solved each:</p>
    </div>

    <!-- Bottleneck 1 -->
    <div style="background: linear-gradient(135deg, rgba(239, 68, 68, 0.08) 0%, rgba(16, 24, 44, 0.95) 100%); border: 1.5px solid rgba(239, 68, 68, 0.4); border-left: 8px solid #EF4444; border-radius: 22px; padding: 28px 32px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
        <span style="font-size: 19px; font-weight: 900; color: #EF4444; letter-spacing: 0.05em; text-transform: uppercase;">01 • The PyTorch Memory Bloat Trap</span>
        <span class="mono" style="font-size: 14px; color: #34D399; font-weight: 800; background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.4); padding: 5px 14px; border-radius: 6px;">SOLUTION: FastEmbed ONNX</span>
      </div>
      <p style="font-size: 20px; color: #CBD5E1; line-height: 1.5; margin-bottom: 14px;">
        <strong style="color: #F87171;">The Trap:</strong> Default <code class="mono" style="color: #F87171;">sentence-transformers</code> loads ~800MB PyTorch wheels. In 1GB serverless containers, cold starts crash instantly from Out-Of-Memory (OOM).
      </p>
      <div style="background: rgba(7, 11, 20, 0.9); border-radius: 12px; padding: 16px 20px; border: 1.5px solid rgba(16, 185, 129, 0.35); font-size: 19px; color: #F1F5F9;">
        <strong style="color: #34D399;">✓ My Production Fix:</strong> Quantized ONNX runtime (<code class="mono">bge-small-en-v1.5</code>). PyTorch stripped completely — cold starts in <strong>2.22s</strong> and peaks at only <strong>423MB RAM</strong> (70% savings).
      </div>
    </div>

    <!-- Bottleneck 2 -->
    <div style="background: linear-gradient(135deg, rgba(245, 158, 11, 0.08) 0%, rgba(16, 24, 44, 0.95) 100%); border: 1.5px solid rgba(245, 158, 11, 0.4); border-left: 8px solid #F59E0B; border-radius: 22px; padding: 28px 32px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
        <span style="font-size: 19px; font-weight: 900; color: #F59E0B; letter-spacing: 0.05em; text-transform: uppercase;">02 • Multi-Tenant Data Leaks</span>
        <span class="mono" style="font-size: 14px; color: #34D399; font-weight: 800; background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.4); padding: 5px 14px; border-radius: 6px;">SOLUTION: Ephemeral RAM</span>
      </div>
      <p style="font-size: 20px; color: #CBD5E1; line-height: 1.5; margin-bottom: 14px;">
        <strong style="color: #F59E0B;">The Trap:</strong> Saving vector collections to local disk files risks leaking confidential clinic documents across sessions and fills container disk space over time.
      </p>
      <div style="background: rgba(7, 11, 20, 0.9); border-radius: 12px; padding: 16px 20px; border: 1.5px solid rgba(16, 185, 129, 0.35); font-size: 19px; color: #F1F5F9;">
        <strong style="color: #34D399;">✓ My Production Fix:</strong> Pure in-memory vector store (<code class="mono">chromadb.EphemeralClient</code>) isolated by session UUIDs with automated LRU memory eviction. Zero disk traces left behind.
      </div>
    </div>

    <!-- Bottleneck 3 -->
    <div style="background: linear-gradient(135deg, rgba(0, 229, 255, 0.08) 0%, rgba(16, 24, 44, 0.95) 100%); border: 1.5px solid rgba(0, 229, 255, 0.4); border-left: 8px solid #00E5FF; border-radius: 22px; padding: 28px 32px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
        <span style="font-size: 19px; font-weight: 900; color: #38BDF8; letter-spacing: 0.05em; text-transform: uppercase;">03 • Hallucinations & Wasted API Spend</span>
        <span class="mono" style="font-size: 14px; color: #34D399; font-weight: 800; background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.4); padding: 5px 14px; border-radius: 6px;">SOLUTION: Vector Math Gate</span>
      </div>
      <p style="font-size: 20px; color: #CBD5E1; line-height: 1.5; margin-bottom: 14px;">
        <strong style="color: #38BDF8;">The Trap:</strong> Passing off-topic questions directly to LLMs burns costly API tokens and risks generating dangerous medical hallucinations.
      </p>
      <div style="background: rgba(7, 11, 20, 0.9); border-radius: 12px; padding: 16px 20px; border: 1.5px solid rgba(16, 185, 129, 0.35); font-size: 19px; color: #F1F5F9;">
        <strong style="color: #34D399;">✓ My Production Fix:</strong> Cosine similarity threshold (<code class="mono">s &gt;= 0.48</code>). Unrelated queries are rejected in <strong>18ms</strong> before invoking the LLM — <strong>$0.00 billed</strong>.
      </div>
    </div>
  </div>

  <div class="footer">
    <div class="footer-name">ClinicDocs AI • Architecture Trade-offs</div>
    <div class="footer-action">Swipe for the system pipeline →</div>
  </div>
</body>
</html>
"""

# -------------------------------------------------------------
# SLIDE 3: THE 4-STAGE PIPELINE (Visual 2x2 Grid)
# -------------------------------------------------------------
slides_html["slide3"] = f"""<!DOCTYPE html>
<html>
<head><style>{CSS_COMMON}</style></head>
<body>
  <div class="top-bar">
    <div class="brand">
      <div class="brand-icon">⚙️</div>
      <div>
        <div class="brand-tag">Modular LCEL Flow</div>
        <div class="brand-title">System Pipeline</div>
      </div>
    </div>
    <div class="slide-counter mono">03 / 05</div>
  </div>

  <div style="flex: 1; display: flex; flex-direction: column; justify-content: space-evenly; padding: 10px 0;">
    <div>
      <div class="pill-badge pill-cyan">Deterministic Architecture</div>
      <h1>Engineered for <span class="gradient-cyan">Sub-Second Speed</span> and Zero Data Leaks</h1>
      <p class="lead-text">Every single pipeline step uses strict type validation, custom exception hierarchies, and automated Pydantic schema validation:</p>
    </div>

    <!-- 4 Pipeline Cards (2x2 Grid) -->
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px;">
      
      <!-- Stage 1 -->
      <div class="card-glow" style="padding: 32px 30px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
          <span class="mono" style="font-size: 14px; font-weight: 800; color: #38BDF8; background: rgba(0, 229, 255, 0.18); padding: 5px 12px; border-radius: 6px;">STAGE 01</span>
          <span class="mono" style="font-size: 13px; color: #94A3B8;">src/ingest.py</span>
        </div>
        <h3 style="font-size: 26px; font-weight: 900; color: #FFFFFF; margin-bottom: 14px;">Deterministic Ingest</h3>
        <ul style="list-style: none; font-size: 18px; color: #CBD5E1; line-height: 1.65;">
          <li style="margin-bottom: 10px;">• <strong style="color: #FFFFFF;">1-Indexed Offset:</strong> PyPDF 0-index corrected to physical document page numbers.</li>
          <li style="margin-bottom: 10px;">• <strong style="color: #FFFFFF;">SHA-256 Hashing:</strong> Byte checksums skip redundant document re-indexing.</li>
          <li>• <strong style="color: #FFFFFF;">Scanned Guard:</strong> Rejects blank scanned image PDFs gracefully.</li>
        </ul>
      </div>

      <!-- Stage 2 -->
      <div class="card-glow" style="padding: 32px 30px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
          <span class="mono" style="font-size: 14px; font-weight: 800; color: #34D399; background: rgba(16, 185, 129, 0.18); padding: 5px 12px; border-radius: 6px;">STAGE 02</span>
          <span class="mono" style="font-size: 13px; color: #94A3B8;">FastEmbed ONNX</span>
        </div>
        <h3 style="font-size: 26px; font-weight: 900; color: #FFFFFF; margin-bottom: 14px;">Quantized Vectors</h3>
        <ul style="list-style: none; font-size: 18px; color: #CBD5E1; line-height: 1.65;">
          <li style="margin-bottom: 10px;">• <strong style="color: #FFFFFF;">Model:</strong> BAAI/bge-small-en-v1.5 quantized embeddings (384-dimensions).</li>
          <li style="margin-bottom: 10px;">• <strong style="color: #FFFFFF;">Zero PyTorch:</strong> Completely eliminates 800MB heavyweight wheels.</li>
          <li>• <strong style="color: #FFFFFF;">Cold Start:</strong> 2.22s embedding init on a standard single-core CPU.</li>
        </ul>
      </div>

      <!-- Stage 3 -->
      <div class="card-glow" style="padding: 32px 30px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
          <span class="mono" style="font-size: 14px; font-weight: 800; color: #F59E0B; background: rgba(245, 158, 11, 0.18); padding: 5px 12px; border-radius: 6px;">STAGE 03</span>
          <span class="mono" style="font-size: 13px; color: #94A3B8;">src/retriever.py</span>
        </div>
        <h3 style="font-size: 26px; font-weight: 900; color: #FFFFFF; margin-bottom: 14px;">In-Memory Isolation</h3>
        <ul style="list-style: none; font-size: 18px; color: #CBD5E1; line-height: 1.65;">
          <li style="margin-bottom: 10px;">• <strong style="color: #FFFFFF;">Zero Disk Retention:</strong> Collections live in RAM via EphemeralClient.</li>
          <li style="margin-bottom: 10px;">• <strong style="color: #FFFFFF;">Session Privacy:</strong> Dedicated collection keys per user UUID.</li>
          <li>• <strong style="color: #FFFFFF;">LRU Eviction:</strong> Old sessions purged after 10 active collections.</li>
        </ul>
      </div>

      <!-- Stage 4 -->
      <div class="card-glow" style="padding: 32px 30px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
          <span class="mono" style="font-size: 14px; font-weight: 800; color: #EC4899; background: rgba(236, 72, 153, 0.18); padding: 5px 12px; border-radius: 6px;">STAGE 04</span>
          <span class="mono" style="font-size: 13px; color: #94A3B8;">src/chain.py</span>
        </div>
        <h3 style="font-size: 26px; font-weight: 900; color: #FFFFFF; margin-bottom: 14px;">Two-Layer Guardrails</h3>
        <ul style="list-style: none; font-size: 18px; color: #CBD5E1; line-height: 1.65;">
          <li style="margin-bottom: 10px;">• <strong style="color: #FFFFFF;">Layer 1 Math Gate:</strong> Cosine similarity halts off-topic queries in 18ms.</li>
          <li style="margin-bottom: 10px;">• <strong style="color: #FFFFFF;">Layer 2 Grounding:</strong> XML prompt sandbox blocks injection attacks.</li>
          <li>• <strong style="color: #FFFFFF;">Smart Rewriting:</strong> Condenses history only from Turn 2 onwards.</li>
        </ul>
      </div>

    </div>
  </div>

  <div class="footer">
    <div class="footer-name">Production Software Architecture • Clean Code</div>
    <div class="footer-action">Swipe to see live dialogue proof →</div>
  </div>
</body>
</html>
"""

# -------------------------------------------------------------
# SLIDE 4: REAL DEMO EVIDENCE (Grounded vs Refused)
# -------------------------------------------------------------
slides_html["slide4"] = f"""<!DOCTYPE html>
<html>
<head><style>{CSS_COMMON}</style></head>
<body>
  <div class="top-bar">
    <div class="brand">
      <div class="brand-icon">🛡️</div>
      <div>
        <div class="brand-tag">Verified Behavior</div>
        <div class="brand-title">Live Query Tests</div>
      </div>
    </div>
    <div class="slide-counter mono">04 / 05</div>
  </div>

  <div style="flex: 1; display: flex; flex-direction: column; justify-content: space-evenly; padding: 10px 0;">
    <div>
      <div class="pill-badge pill-emerald">Live Interrogation Test</div>
      <h1>Strict Grounding vs <span class="gradient-coral">Zero-Token Refusal</span></h1>
      <p class="lead-text">Two real side-by-side test cases showing how the system answers clinical policy questions versus rejecting out-of-scope trick queries:</p>
    </div>

    <!-- Test Case 1: Grounded -->
    <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(16, 26, 48, 0.95) 100%); border: 2px solid rgba(16, 185, 129, 0.45); border-radius: 24px; padding: 30px 32px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
        <span class="mono" style="font-size: 15px; font-weight: 800; color: #34D399; background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.4); padding: 6px 14px; border-radius: 8px;">✓ TEST 1: IN-DOMAIN CLINICAL QUERY</span>
        <span class="mono" style="font-size: 15px; color: #94A3B8; font-weight: 600;">Latency: 0.94s • 100% Grounded</span>
      </div>
      <div style="background: rgba(255, 255, 255, 0.05); border-radius: 14px; padding: 16px 20px; margin-bottom: 16px; font-size: 20px; color: #FFFFFF;">
        <span class="mono" style="color: #38BDF8; font-weight: 800;">User Query: </span>"How much is a specialist consultation, and what is the follow-up policy?"
      </div>
      <div style="background: rgba(7, 11, 20, 0.95); border-radius: 14px; padding: 20px 22px; border: 1.5px solid rgba(255, 255, 255, 0.08); font-size: 19px; color: #E2E8F0; line-height: 1.55;">
        A consultation with a Specialist Doctor (Cardiologist, Pediatrician, Dermatologist) costs <strong style="color: #FFFFFF;">PKR 3,000</strong>. Follow-up visits within 7 days of the initial consultation receive a <strong style="color: #34D399;">50% discount (PKR 1,500)</strong>.
        <div style="margin-top: 16px; padding-top: 14px; border-top: 1.5px solid rgba(255, 255, 255, 0.08); display: flex; justify-content: space-between; align-items: center; font-size: 15px;">
          <span class="mono" style="color: #F8FAFC;">📄 Clinic_Fee_Schedule_2026.pdf <strong style="color: #34D399; font-weight: 800;">— Page 2</strong></span>
          <span class="mono" style="color: #38BDF8; font-weight: 800;">Cosine Match: 81.4%</span>
        </div>
      </div>
    </div>

    <!-- Test Case 2: Refused -->
    <div style="background: linear-gradient(135deg, rgba(248, 113, 113, 0.08) 0%, rgba(28, 16, 24, 0.95) 100%); border: 2px solid rgba(248, 113, 113, 0.45); border-radius: 24px; padding: 30px 32px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
        <span class="mono" style="font-size: 15px; font-weight: 800; color: #F87171; background: rgba(248, 113, 113, 0.15); border: 1px solid rgba(248, 113, 113, 0.4); padding: 6px 14px; border-radius: 8px;">🛡️ TEST 2: OUT-OF-DOMAIN TRICK QUERY</span>
        <span class="mono" style="font-size: 15px; color: #F87171; font-weight: 800;">⚡ 18ms Refusal • $0.00 Spent</span>
      </div>
      <div style="background: rgba(255, 255, 255, 0.05); border-radius: 14px; padding: 16px 20px; margin-bottom: 16px; font-size: 20px; color: #FFFFFF;">
        <span class="mono" style="color: #F87171; font-weight: 800;">User Query: </span>"What is the capital city of France?"
      </div>
      <div style="background: rgba(7, 11, 20, 0.95); border-radius: 14px; padding: 20px 22px; border: 1.5px solid rgba(255, 255, 255, 0.08); font-size: 19px; color: #E2E8F0; line-height: 1.55;">
        <div style="color: #F87171; font-weight: 800; font-size: 20px; margin-bottom: 8px;">"I couldn't find this in the uploaded documents."</div>
        <div style="font-size: 16px; color: #94A3B8; line-height: 1.55;">
          Max observed cosine similarity: <span class="mono" style="color: #FFFFFF; font-weight: 700;">0.361 &lt; 0.48 threshold</span>. The query was intercepted at the vector stage. Zero LLM API calls made. <strong style="color: #34D399;">0 tokens billed.</strong>
        </div>
      </div>
    </div>

  </div>

  <div class="footer">
    <div class="footer-name">Zero Hallucinations Guarantee • Security Guardrails</div>
    <div class="footer-action">Swipe for benchmark stats →</div>
  </div>
</body>
</html>
"""

# -------------------------------------------------------------
# SLIDE 5: MEASURED TELEMETRY & AUTHOR CARD (Balanced Vertical Space)
# -------------------------------------------------------------
slides_html["slide5"] = f"""<!DOCTYPE html>
<html>
<head><style>{CSS_COMMON}</style></head>
<body>
  <div class="top-bar">
    <div class="brand">
      <div class="brand-icon">📊</div>
      <div>
        <div class="brand-tag">Measured Telemetry</div>
        <div class="brand-title">Production Benchmarks</div>
      </div>
    </div>
    <div class="slide-counter mono">05 / 05</div>
  </div>

  <div style="flex: 1; display: flex; flex-direction: column; justify-content: space-evenly; padding: 10px 0;">
    <div>
      <div class="pill-badge pill-emerald">Single Core CPU Telemetry</div>
      <h1>Hard Data Beats <span class="gradient-emerald">Portfolio Claims</span></h1>
      <p class="lead-text">Measured live under container resource constraints using automated telemetry scripts:</p>
    </div>

    <!-- Benchmark Table -->
    <div style="background: rgba(13, 20, 36, 0.85); border-radius: 22px; overflow: hidden; border: 1.5px solid rgba(255, 255, 255, 0.15);">
      <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 18px;">
        <thead>
          <tr style="background: rgba(255, 255, 255, 0.06); border-bottom: 1.5px solid rgba(255, 255, 255, 0.12);">
            <th style="padding: 20px 26px; color: #94A3B8; font-weight: 800; text-transform: uppercase; font-size: 15px; letter-spacing: 0.06em;">Engineering Metric</th>
            <th style="padding: 20px 26px; color: #38BDF8; font-weight: 900; text-transform: uppercase; font-size: 15px; letter-spacing: 0.06em;">ClinicDocs AI</th>
            <th style="padding: 20px 26px; color: #64748B; font-weight: 800; text-transform: uppercase; font-size: 15px; letter-spacing: 0.06em;">Naive PyTorch RAG</th>
            <th style="padding: 20px 26px; color: #34D399; font-weight: 900; text-transform: uppercase; font-size: 15px; letter-spacing: 0.06em;">Impact</th>
          </tr>
        </thead>
        <tbody class="mono">
          <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.06);">
            <td style="padding: 19px 26px; color: #E2E8F0; font-family: -apple-system, BlinkMacSystemFont, sans-serif; font-size: 18px;">Embedding Model RAM</td>
            <td style="padding: 19px 26px; color: #38BDF8; font-weight: 800;">136.2 MB</td>
            <td style="padding: 19px 26px; color: #64748B;">850+ MB</td>
            <td style="padding: 19px 26px; color: #34D399; font-weight: 800;">-84% Less RAM</td>
          </tr>
          <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.06); background: rgba(255, 255, 255, 0.02);">
            <td style="padding: 19px 26px; color: #E2E8F0; font-family: -apple-system, BlinkMacSystemFont, sans-serif; font-size: 18px;">Total Process Peak RAM</td>
            <td style="padding: 19px 26px; color: #38BDF8; font-weight: 800;">423.2 MB</td>
            <td style="padding: 19px 26px; color: #EF4444; font-weight: 700;">1,420 MB (OOM Risk)</td>
            <td style="padding: 19px 26px; color: #34D399; font-weight: 800;">Fits 1GB Cap</td>
          </tr>
          <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.06);">
            <td style="padding: 19px 26px; color: #E2E8F0; font-family: -apple-system, BlinkMacSystemFont, sans-serif; font-size: 18px;">Out-of-Domain Refusal</td>
            <td style="padding: 19px 26px; color: #38BDF8; font-weight: 800;">&lt; 25 ms</td>
            <td style="padding: 19px 26px; color: #64748B;">2,850 ms (Full LLM)</td>
            <td style="padding: 19px 26px; color: #34D399; font-weight: 800;">99% Faster</td>
          </tr>
          <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.06); background: rgba(255, 255, 255, 0.02);">
            <td style="padding: 19px 26px; color: #E2E8F0; font-family: -apple-system, BlinkMacSystemFont, sans-serif; font-size: 18px;">Cost on Trick Questions</td>
            <td style="padding: 19px 26px; color: #34D399; font-weight: 800;">$0.00 (0 Tokens)</td>
            <td style="padding: 19px 26px; color: #EF4444;">Standard API Rates</td>
            <td style="padding: 19px 26px; color: #34D399; font-weight: 800;">Zero Cost</td>
          </tr>
          <tr>
            <td style="padding: 19px 26px; color: #E2E8F0; font-family: -apple-system, BlinkMacSystemFont, sans-serif; font-size: 18px;">Benchmark Eval Score</td>
            <td style="padding: 19px 26px; color: #34D399; font-weight: 900;">10 / 10 Passed</td>
            <td style="padding: 19px 26px; color: #EF4444;">Hallucinations</td>
            <td style="padding: 19px 26px; color: #34D399; font-weight: 800;">100% Grounded</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Author Profile & CTA Card -->
    <div class="card-glow" style="display: flex; justify-content: space-between; align-items: center; padding: 28px 34px;">
      <div style="display: flex; align-items: center; gap: 20px;">
        <div style="width: 64px; height: 64px; border-radius: 18px; background: linear-gradient(135deg, #00E5FF, #3B82F6); display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 24px; color: #FFFFFF; border: 2px solid rgba(255, 255, 255, 0.3); box-shadow: 0 4px 20px rgba(0, 229, 255, 0.4);">
          FAN
        </div>
        <div>
          <div style="font-size: 24px; font-weight: 900; color: #FFFFFF;">Farwa Ali Nasir</div>
          <div style="font-size: 17px; color: #38BDF8; font-weight: 700; margin-top: 2px;">AI & Machine Learning Software Engineer</div>
          <div style="font-size: 14px; color: #94A3B8; margin-top: 4px;">Open to Full-Time & Associate AI/ML & SWE Roles</div>
        </div>
      </div>
      <div style="text-align: right;">
        <div class="mono" style="font-size: 16px; color: #34D399; font-weight: 800;">Live Demo & Code 👇</div>
        <div class="mono" style="font-size: 13px; color: #94A3B8; margin-top: 4px;">github.com/farwanasir2810-collab</div>
      </div>
    </div>
  </div>

  <div class="footer">
    <div class="footer-name">Open-Source Healthcare AI Solution</div>
    <div class="footer-action" style="color: #34D399;">Test live app in comments! 🚀</div>
  </div>
</body>
</html>
"""

# Render each slide using Chrome headless
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
image_paths = []

for name, html in slides_html.items():
    html_path = os.path.join(OUTPUT_DIR, f"{name}.html")
    img_path = os.path.join(OUTPUT_DIR, f"{name}.jpg")
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
        
    print(f"Rendering {name} (1080x1350)...")
    cmd = [
        chrome_path,
        "--headless",
        "--disable-gpu",
        "--hide-scrollbars",
        "--window-size=1080,1350",
        f"--screenshot={img_path}",
        html_path
    ]
    subprocess.run(cmd, check=True)
    image_paths.append(img_path)
    print(f"Successfully rendered: {img_path}")

# Build multi-page PDF
pdf_path = os.path.join(OUTPUT_DIR, "ClinicDocs_AI_CaseStudy.pdf")
images = [Image.open(p).convert("RGB") for p in image_paths]
images[0].save(pdf_path, save_all=True, append_images=images[1:], resolution=100.0)
print(f"Successfully compiled 4:5 PDF Carousel: {pdf_path}")
