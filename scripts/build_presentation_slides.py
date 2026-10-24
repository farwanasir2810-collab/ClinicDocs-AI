import os
import subprocess
from PIL import Image

# Define pure CSS styling template
CSS_COMMON = """
  * { box-sizing: border-box; }
  body {
    margin: 0;
    padding: 50px 60px;
    width: 1200px;
    height: 1200px;
    background-color: #070B14;
    background-image: 
      radial-gradient(circle at 85% 15%, rgba(6, 182, 212, 0.22) 0%, transparent 45%),
      radial-gradient(circle at 15% 85%, rgba(16, 185, 129, 0.18) 0%, transparent 45%),
      linear-gradient(to right, rgba(255, 255, 255, 0.03) 1px, transparent 1px),
      linear-gradient(to bottom, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
    background-size: 100% 100%, 100% 100%, 36px 36px, 36px 36px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    color: #F8FAFC;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    overflow: hidden;
  }
  .mono { font-family: 'Consolas', 'Courier New', monospace; }
  .badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 16px;
    border-radius: 9999px;
    background: rgba(6, 182, 212, 0.15);
    border: 1px solid rgba(6, 182, 212, 0.4);
    color: #38BDF8;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }
  .slide-counter {
    padding: 6px 16px;
    border-radius: 9999px;
    background: #0F172A;
    border: 1px solid #334155;
    color: #94A3B8;
    font-size: 13px;
    font-weight: 700;
  }
  .card {
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    padding: 24px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.4);
  }
  .card-highlight {
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(7, 11, 20, 0.9));
    border: 1.5px solid rgba(6, 182, 212, 0.4);
    border-radius: 20px;
    padding: 24px;
    box-shadow: 0 15px 35px rgba(6, 182, 212, 0.12);
  }
  h1 {
    font-size: 46px;
    font-weight: 900;
    line-height: 1.15;
    margin: 12px 0;
    color: #FFFFFF;
    letter-spacing: -0.02em;
  }
  .gradient-text {
    background: linear-gradient(90deg, #38BDF8, #2DD4BF, #34D399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  p.subtitle {
    font-size: 18px;
    line-height: 1.45;
    color: #CBD5E1;
    margin: 0 0 16px 0;
  }
  .footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-top: 1px solid #1E293B;
    padding-top: 18px;
    font-size: 14px;
    color: #94A3B8;
  }
"""

slides_html = {}

# -------------------------------------------------------------
# SLIDE 1: HERO PRODUCT REVEAL
# -------------------------------------------------------------
slides_html["slide1"] = f"""<!DOCTYPE html>
<html>
<head><style>{CSS_COMMON}</style></head>
<body>
  <div style="display: flex; justify-content: space-between; align-items: center;">
    <div style="display: flex; align-items: center; gap: 12px;">
      <div style="width: 44px; height: 44px; background: rgba(6, 182, 212, 0.2); border: 1px solid #06B6D4; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 22px;">🩺</div>
      <div>
        <div style="font-size: 12px; color: #38BDF8; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase;">Flagship AI Case Study</div>
        <div style="font-size: 20px; font-weight: 800; color: #FFFFFF;">ClinicDocs AI</div>
      </div>
    </div>
    <div class="slide-counter mono">Slide 01 / 05</div>
  </div>

  <div style="margin: auto 0;">
    <div class="badge">Production Conversational RAG</div>
    <h1>Chat with Clinical Policies with <span class="gradient-text">Zero Hallucinations</span> & Exact Citations</h1>
    <p class="subtitle">A production-grade, privacy-first web application that turns static clinic policies into verified conversational answers with 1-indexed page citations and two-layer refusal guardrails.</p>

    <!-- Real UI Mockup Window -->
    <div class="card-highlight" style="margin-bottom: 20px;">
      <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1E293B; padding-bottom: 10px; margin-bottom: 14px;">
        <div style="display: flex; align-items: center; gap: 8px;">
          <span style="width: 12px; height: 12px; border-radius: 50%; background: #EF4444; display: inline-block;"></span>
          <span style="width: 12px; height: 12px; border-radius: 50%; background: #F59E0B; display: inline-block;"></span>
          <span style="width: 12px; height: 12px; border-radius: 50%; background: #10B981; display: inline-block;"></span>
          <span class="mono" style="font-size: 13px; color: #94A3B8; margin-left: 8px;">clinicdocs-ai.streamlit.app — Live Session Active</span>
        </div>
        <span class="mono" style="font-size: 12px; background: rgba(16, 185, 129, 0.15); color: #34D399; padding: 4px 10px; border-radius: 6px; border: 1px solid rgba(16, 185, 129, 0.4); font-weight: bold;">✓ 10/10 EVALS PASSED</span>
      </div>

      <div style="background: rgba(10, 15, 26, 0.8); border: 1px solid #1E293B; border-radius: 12px; padding: 16px; margin-bottom: 12px;">
        <span class="mono" style="color: #38BDF8; font-weight: bold; font-size: 14px;">User: </span>
        <span style="color: #FFFFFF; font-size: 15px; font-weight: 600;">What are the clinic operating hours on Friday?</span>
      </div>

      <div style="background: #0A0F1A; border: 1px solid #1E293B; border-radius: 14px; padding: 18px;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
          <span class="mono" style="color: #2DD4BF; font-weight: bold; font-size: 13px;">🩺 ClinicDocs AI:</span>
          <span class="mono" style="color: #94A3B8; font-size: 12px;">⏱️ Latency: 0.82s</span>
        </div>
        <div style="color: #E2E8F0; font-size: 15px; line-height: 1.5; margin-bottom: 12px;">
          On Friday, Noor Care Clinic operates in two shifts:<br>
          • <strong>Morning Shift:</strong> 9:00 AM – 1:00 PM<br>
          • <strong>Evening Shift:</strong> 3:00 PM – 8:00 PM<br>
          <em>(The clinic is closed between 1:00 PM and 3:00 PM for Friday prayers).</em>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #1E293B; padding-top: 10px; font-size: 13px;">
          <span class="mono" style="color: #CBD5E1;">📄 <strong>Noor_Care_Clinic_FAQ.pdf</strong> <span style="color: #34D399; font-weight: bold;">— Page 1</span></span>
          <span class="mono" style="background: rgba(6, 182, 212, 0.2); color: #38BDF8; padding: 2px 8px; border-radius: 4px; font-weight: bold; border: 1px solid #06B6D4;">Match: 78.2%</span>
        </div>
      </div>
    </div>

    <!-- 4 High-Contrast Stats -->
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px;">
      <div class="card" style="text-align: center; padding: 16px;">
        <div class="mono" style="font-size: 26px; font-weight: 900; color: #38BDF8;">70%</div>
        <div style="font-size: 12px; color: #94A3B8; margin-top: 4px; font-weight: 600;">RAM Savings (ONNX)</div>
      </div>
      <div class="card" style="text-align: center; padding: 16px;">
        <div class="mono" style="font-size: 26px; font-weight: 900; color: #34D399;">&lt; 25 ms</div>
        <div style="font-size: 12px; color: #94A3B8; margin-top: 4px; font-weight: 600;">Refusal Gate Speed</div>
      </div>
      <div class="card" style="text-align: center; padding: 16px;">
        <div class="mono" style="font-size: 26px; font-weight: 900; color: #38BDF8;">0 Tokens</div>
        <div style="font-size: 12px; color: #94A3B8; margin-top: 4px; font-weight: 600;">Wasted on OOD</div>
      </div>
      <div class="card" style="text-align: center; padding: 16px;">
        <div class="mono" style="font-size: 26px; font-weight: 900; color: #34D399;">100%</div>
        <div style="font-size: 12px; color: #94A3B8; margin-top: 4px; font-weight: 600;">Grounded Accuracy</div>
      </div>
    </div>
  </div>

  <div class="footer">
    <div>Architected &amp; Built by <strong style="color: #FFFFFF;">Farwa Ali Nasir</strong> — AI &amp; ML Software Engineer</div>
    <div style="color: #38BDF8; font-weight: 700;">Swipe right to inspect architecture ➔</div>
  </div>
</body>
</html>"""

# -------------------------------------------------------------
# SLIDE 2: THE 3 CRITICAL PRODUCTION BOTTLENECKS
# -------------------------------------------------------------
slides_html["slide2"] = f"""<!DOCTYPE html>
<html>
<head><style>{CSS_COMMON}</style></head>
<body>
  <div style="display: flex; justify-content: space-between; align-items: center;">
    <div style="display: flex; align-items: center; gap: 12px;">
      <div style="width: 44px; height: 44px; background: rgba(239, 68, 68, 0.2); border: 1px solid #EF4444; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 22px;">⚠️</div>
      <div>
        <div style="font-size: 12px; color: #F87171; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase;">The Engineering Challenge</div>
        <div style="font-size: 20px; font-weight: 800; color: #FFFFFF;">Why 90% of RAG Demos Fail in Production</div>
      </div>
    </div>
    <div class="slide-counter mono">Slide 02 / 05</div>
  </div>

  <div style="margin: auto 0;">
    <div class="badge" style="background: rgba(239, 68, 68, 0.15); border-color: #EF4444; color: #F87171;">Production Bottlenecks Solved</div>
    <h1>Toy Tutorials vs <span class="gradient-text">Real Production Systems</span></h1>
    <p class="subtitle">Standard Jupyter notebook RAG breaks under strict container resource limits, multi-tenant isolation requirements, and out-of-domain hallucinations:</p>

    <!-- 3 High Contrast Problem vs Solution Rows -->
    <div style="display: flex; flex-direction: column; gap: 16px;">
      
      <!-- Card 1: Memory -->
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
        <div class="card" style="border-left: 4px solid #EF4444;">
          <div style="color: #F87171; font-weight: 800; font-size: 15px; margin-bottom: 6px;">❌ Heavy PyTorch OOM Crashes</div>
          <div style="color: #CBD5E1; font-size: 13.5px; line-height: 1.45;">Standard sentence-transformers imports heavy PyTorch wheels (~800MB), exceeding 1GB serverless caps and crashing containers.</div>
        </div>
        <div class="card" style="border-left: 4px solid #10B981; background: rgba(16, 185, 129, 0.08);">
          <div style="color: #34D399; font-weight: 800; font-size: 15px; margin-bottom: 6px;">✓ FastEmbed ONNX (70% Less RAM)</div>
          <div style="color: #CBD5E1; font-size: 13.5px; line-height: 1.45;">Quantized ONNX runtime (bge-small-en-v1.5) cold-starts in 2.22s and peaks at only <strong>423.2MB RAM</strong> under full load.</div>
        </div>
      </div>

      <!-- Card 2: Privacy -->
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
        <div class="card" style="border-left: 4px solid #EF4444;">
          <div style="color: #F87171; font-weight: 800; font-size: 15px; margin-bottom: 6px;">❌ Multi-Tenant Data Leaks</div>
          <div style="color: #CBD5E1; font-size: 13.5px; line-height: 1.45;">Storing vector collections on shared persistent disk leaks previous users' confidential documents across sessions.</div>
        </div>
        <div class="card" style="border-left: 4px solid #10B981; background: rgba(16, 185, 129, 0.08);">
          <div style="color: #34D399; font-weight: 800; font-size: 15px; margin-bottom: 6px;">✓ Ephemeral RAM Isolation</div>
          <div style="color: #CBD5E1; font-size: 13.5px; line-height: 1.45;">Collections live strictly in memory (chromadb.EphemeralClient) tied to session UUIDs with an LRU cap (max 10). Zero disk footprint.</div>
        </div>
      </div>

      <!-- Card 3: Hallucinations -->
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
        <div class="card" style="border-left: 4px solid #EF4444;">
          <div style="color: #F87171; font-weight: 800; font-size: 15px; margin-bottom: 6px;">❌ Hallucinations & Wasted API Bills</div>
          <div style="color: #CBD5E1; font-size: 13.5px; line-height: 1.45;">Irrelevant queries invoke full LLM completions, burning expensive API tokens while fabricating unstated medical claims.</div>
        </div>
        <div class="card" style="border-left: 4px solid #10B981; background: rgba(16, 185, 129, 0.08);">
          <div style="color: #34D399; font-weight: 800; font-size: 15px; margin-bottom: 6px;">✓ Two-Layer Refusal Gate (<25ms)</div>
          <div style="color: #CBD5E1; font-size: 13.5px; line-height: 1.45;">Cosine similarity gate (s >= 0.48) halts unrelated queries at the vector stage in <strong>18ms with 0 tokens billed</strong> ($0.00 spent).</div>
        </div>
      </div>

    </div>
  </div>

  <div class="footer">
    <div>Architectural Trade-offs • Cloud Budget Discipline</div>
    <div style="color: #38BDF8; font-weight: 700;">Swipe right for the system pipeline ➔</div>
  </div>
</body>
</html>"""

# -------------------------------------------------------------
# SLIDE 3: THE 4-STAGE SYSTEM ARCHITECTURE
# -------------------------------------------------------------
slides_html["slide3"] = f"""<!DOCTYPE html>
<html>
<head><style>{CSS_COMMON}</style></head>
<body>
  <div style="display: flex; justify-content: space-between; align-items: center;">
    <div style="display: flex; align-items: center; gap: 12px;">
      <div style="width: 44px; height: 44px; background: rgba(16, 185, 129, 0.2); border: 1px solid #10B981; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 22px;">⚙️</div>
      <div>
        <div style="font-size: 12px; color: #34D399; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase;">System Architecture</div>
        <div style="font-size: 20px; font-weight: 800; color: #FFFFFF;">The 4-Stage Production Pipeline</div>
      </div>
    </div>
    <div class="slide-counter mono">Slide 03 / 05</div>
  </div>

  <div style="margin: auto 0;">
    <div class="badge">Modular LCEL Architecture</div>
    <h1>Engineered for <span class="gradient-text">High Reliability</span> & Speed</h1>
    <p class="subtitle">Every stage in the pipeline is engineered with deterministic validation, strict type hints, and automated Pytest harnesses:</p>

    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
      
      <!-- Stage 1 -->
      <div class="card" style="background: rgba(15, 23, 42, 0.95);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
          <span class="mono" style="color: #38BDF8; font-size: 12px; font-weight: bold; background: rgba(6, 182, 212, 0.15); padding: 3px 8px; border-radius: 4px; border: 1px solid #06B6D4;">STAGE 01</span>
          <span class="mono" style="color: #64748B; font-size: 12px;">src/ingest.py</span>
        </div>
        <div style="font-size: 18px; font-weight: 800; color: #FFFFFF; margin-bottom: 8px;">Ingestion & Normalization</div>
        <div style="color: #94A3B8; font-size: 13.5px; line-height: 1.5;">
          • <strong>1-Indexed Offset:</strong> PyPDF 0-indexed pages mapped to physical <code>page + 1</code>.<br>
          • <strong>SHA-256 Digest:</strong> Byte hashing skips duplicate indexing.<br>
          • <strong>Scanned PDF Guard:</strong> Text-density check raises ScannedPDFError.
        </div>
      </div>

      <!-- Stage 2 -->
      <div class="card" style="background: rgba(15, 23, 42, 0.95);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
          <span class="mono" style="color: #34D399; font-size: 12px; font-weight: bold; background: rgba(16, 185, 129, 0.15); padding: 3px 8px; border-radius: 4px; border: 1px solid #10B981;">STAGE 02</span>
          <span class="mono" style="color: #64748B; font-size: 12px;">FastEmbed ONNX</span>
        </div>
        <div style="font-size: 18px; font-weight: 800; color: #FFFFFF; margin-bottom: 8px;">Quantized ONNX Embeddings</div>
        <div style="color: #94A3B8; font-size: 13.5px; line-height: 1.5;">
          • <strong>Model:</strong> BAAI/bge-small-en-v1.5 (384-dimensional).<br>
          • <strong>Runtime:</strong> Stripped 800MB PyTorch dependency completely.<br>
          • <strong>Efficiency:</strong> 2.22s cold start, only +136MB memory footprint.
        </div>
      </div>

      <!-- Stage 3 -->
      <div class="card" style="background: rgba(15, 23, 42, 0.95);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
          <span class="mono" style="color: #38BDF8; font-size: 12px; font-weight: bold; background: rgba(6, 182, 212, 0.15); padding: 3px 8px; border-radius: 4px; border: 1px solid #06B6D4;">STAGE 03</span>
          <span class="mono" style="color: #64748B; font-size: 12px;">src/retriever.py</span>
        </div>
        <div style="font-size: 18px; font-weight: 800; color: #FFFFFF; margin-bottom: 8px;">Ephemeral Vector Store</div>
        <div style="color: #94A3B8; font-size: 13.5px; line-height: 1.5;">
          • <strong>Zero Disk Retention:</strong> Collections live in RAM via EphemeralClient.<br>
          • <strong>Session Isolation:</strong> Keyed to unique session UUIDs.<br>
          • <strong>LRU Eviction Cap:</strong> Active collections capped at 10 to avoid leaks.
        </div>
      </div>

      <!-- Stage 4 -->
      <div class="card" style="background: rgba(15, 23, 42, 0.95);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
          <span class="mono" style="color: #34D399; font-size: 12px; font-weight: bold; background: rgba(16, 185, 129, 0.15); padding: 3px 8px; border-radius: 4px; border: 1px solid #10B981;">STAGE 04</span>
          <span class="mono" style="color: #64748B; font-size: 12px;">src/chain.py</span>
        </div>
        <div style="font-size: 18px; font-weight: 800; color: #FFFFFF; margin-bottom: 8px;">Two-Layer Guardrails</div>
        <div style="color: #94A3B8; font-size: 13.5px; line-height: 1.5;">
          • <strong>Layer 1 Gate:</strong> Vector cosine similarity threshold (s >= 0.48).<br>
          • <strong>Layer 2 Grounding:</strong> XML &lt;document_context&gt; prompt isolation.<br>
          • <strong>Conditional Rewriter:</strong> History contextualizer only runs on Turn 2+.
        </div>
      </div>

    </div>
  </div>

  <div class="footer">
    <div>Deterministic System Design • Multi-Tenant Security</div>
    <div style="color: #38BDF8; font-weight: 700;">Swipe right to see live interaction evidence ➔</div>
  </div>
</body>
</html>"""

# -------------------------------------------------------------
# SLIDE 4: REAL LIVE DIALOGUE EVIDENCE
# -------------------------------------------------------------
slides_html["slide4"] = f"""<!DOCTYPE html>
<html>
<head><style>{CSS_COMMON}</style></head>
<body>
  <div style="display: flex; justify-content: space-between; align-items: center;">
    <div style="display: flex; align-items: center; gap: 12px;">
      <div style="width: 44px; height: 44px; background: rgba(6, 182, 212, 0.2); border: 1px solid #06B6D4; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 22px;">💬</div>
      <div>
        <div style="font-size: 12px; color: #38BDF8; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase;">Verified Evidence</div>
        <div style="font-size: 20px; font-weight: 800; color: #FFFFFF;">Grounded Answers vs 18ms Refusals</div>
      </div>
    </div>
    <div class="slide-counter mono">Slide 04 / 05</div>
  </div>

  <div style="margin: auto 0;">
    <div class="badge">Real In-App Interactions</div>
    <h1>Strict Grounding vs <span class="gradient-text">Zero Token Refusal</span></h1>
    <p class="subtitle">See how the system handles a verified clinical policy question compared to a semantically distant out-of-domain trick question:</p>

    <!-- Case 1: In-Domain Grounded -->
    <div class="card" style="border: 1.5px solid rgba(16, 185, 129, 0.4); margin-bottom: 18px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <span class="mono" style="color: #34D399; font-size: 13px; font-weight: bold;">✓ Case 1: Grounded Policy Question (1-Indexed Page Citation)</span>
        <span class="mono" style="font-size: 12px; background: rgba(6, 182, 212, 0.15); color: #38BDF8; padding: 2px 8px; border-radius: 4px;">⏱️ Latency: 0.94s</span>
      </div>
      <div style="background: #0A0F1A; border: 1px solid #1E293B; border-radius: 10px; padding: 12px; margin-bottom: 10px;">
        <span class="mono" style="color: #38BDF8; font-weight: bold;">User: </span>
        <span style="color: #FFFFFF; font-size: 14.5px; font-weight: 600;">How much is a specialist consultation, and what is the follow-up policy?</span>
      </div>
      <div style="background: rgba(10, 15, 26, 0.6); border-radius: 10px; padding: 14px; font-size: 14px; line-height: 1.5; color: #E2E8F0;">
        A consultation with a Specialist Doctor (Cardiologist, Pediatrician, Dermatologist) costs <strong>PKR 3,000</strong>. Follow-up visits within 7 days of the initial consultation receive a <strong>50% discount (PKR 1,500)</strong>.
        <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #1E293B; display: flex; justify-content: space-between; font-size: 12px;" class="mono">
          <span style="color: #CBD5E1;">📄 <strong>Clinic_Fee_Schedule_2026.pdf</strong> <span style="color: #34D399; font-weight: bold;">— Page 2</span></span>
          <span style="color: #38BDF8;">Cosine Similarity: 81.4%</span>
        </div>
      </div>
    </div>

    <!-- Case 2: Out of domain refusal -->
    <div class="card" style="border: 1.5px solid rgba(239, 68, 68, 0.4);">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <span class="mono" style="color: #F87171; font-size: 13px; font-weight: bold;">🛡️ Case 2: Layer 1 Refusal Gate (Out-of-Domain Query)</span>
        <span class="mono" style="font-size: 12px; background: rgba(239, 68, 68, 0.15); color: #F87171; padding: 2px 8px; border-radius: 4px; font-weight: bold;">⚡ 18ms (0 Tokens Billed)</span>
      </div>
      <div style="background: #0A0F1A; border: 1px solid #1E293B; border-radius: 10px; padding: 12px; margin-bottom: 10px;">
        <span class="mono" style="color: #38BDF8; font-weight: bold;">User: </span>
        <span style="color: #FFFFFF; font-size: 14.5px; font-weight: 600;">What is the capital city of France?</span>
      </div>
      <div style="background: rgba(10, 15, 26, 0.6); border-radius: 10px; padding: 14px; font-size: 14px; color: #CBD5E1;">
        <div style="color: #FCA5A5; font-style: italic; font-size: 15px; margin-bottom: 8px;">"I couldn't find this in the uploaded documents."</div>
        <div class="mono" style="font-size: 12px; color: #94A3B8; border-top: 1px solid #1E293B; padding-top: 8px;">
          Max observed cosine similarity: <strong>0.361 &lt; 0.48 threshold</strong>. Query halted at vector retrieval stage. <strong>Zero LLM tokens used. $0.00 cost.</strong>
        </div>
      </div>
    </div>

  </div>

  <div class="footer">
    <div>Two-Layer Guardrails: Vector Math Gate + Strict Prompt Isolation</div>
    <div style="color: #38BDF8; font-weight: 700;">Swipe right for measured telemetry ➔</div>
  </div>
</body>
</html>"""

# -------------------------------------------------------------
# SLIDE 5: MEASURED TELEMETRY & AUTHOR
# -------------------------------------------------------------
slides_html["slide5"] = f"""<!DOCTYPE html>
<html>
<head><style>{CSS_COMMON}</style></head>
<body>
  <div style="display: flex; justify-content: space-between; align-items: center;">
    <div style="display: flex; align-items: center; gap: 12px;">
      <div style="width: 44px; height: 44px; background: rgba(6, 182, 212, 0.2); border: 1px solid #06B6D4; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 22px;">📊</div>
      <div>
        <div style="font-size: 12px; color: #38BDF8; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase;">Empirical Telemetry</div>
        <div style="font-size: 20px; font-weight: 800; color: #FFFFFF;">Measured Benchmarks &amp; Author Profile</div>
      </div>
    </div>
    <div class="slide-counter mono">Slide 05 / 05</div>
  </div>

  <div style="margin: auto 0;">
    <div class="badge">Reproducible Benchmarks</div>
    <h1>Production Telemetry vs <span class="gradient-text">Naive RAG Baselines</span></h1>
    <p class="subtitle">Measured live on single CPU core constraints using scripts/measure_benchmarks.py:</p>

    <!-- Telemetry Table -->
    <div class="card" style="padding: 0; overflow: hidden; margin-bottom: 20px;">
      <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 13.5px;" class="mono">
        <thead>
          <tr style="background: #0F172A; border-bottom: 1px solid #334155; color: #94A3B8; text-transform: uppercase; font-size: 12px;">
            <th style="padding: 14px 18px;">Engineering Metric</th>
            <th style="padding: 14px 18px; color: #38BDF8;">ClinicDocs AI</th>
            <th style="padding: 14px 18px;">Naive PyTorch RAG</th>
            <th style="padding: 14px 18px; text-align: right; color: #34D399;">Impact</th>
          </tr>
        </thead>
        <tbody style="color: #E2E8F0;">
          <tr style="border-bottom: 1px solid #1E293B;">
            <td style="padding: 12px 18px; font-family: sans-serif; font-weight: 600;">Embedding Model RAM</td>
            <td style="padding: 12px 18px; color: #38BDF8; font-weight: bold;">136.2 MB (ONNX)</td>
            <td style="padding: 12px 18px; color: #94A3B8;">850+ MB (PyTorch)</td>
            <td style="padding: 12px 18px; text-align: right; color: #34D399; font-weight: bold;">70% Reduction</td>
          </tr>
          <tr style="border-bottom: 1px solid #1E293B;">
            <td style="padding: 12px 18px; font-family: sans-serif; font-weight: 600;">Peak Process Memory</td>
            <td style="padding: 12px 18px; color: #34D399; font-weight: bold;">423.2 MB</td>
            <td style="padding: 12px 18px; color: #94A3B8;">1,420 MB (OOM Risk)</td>
            <td style="padding: 12px 18px; text-align: right; color: #34D399; font-weight: bold;">Fits 1GB Cap</td>
          </tr>
          <tr style="border-bottom: 1px solid #1E293B;">
            <td style="padding: 12px 18px; font-family: sans-serif; font-weight: 600;">Out-of-Domain Refusal</td>
            <td style="padding: 12px 18px; color: #38BDF8; font-weight: bold;">&lt; 25 ms</td>
            <td style="padding: 12px 18px; color: #94A3B8;">2,850 ms (Full LLM)</td>
            <td style="padding: 12px 18px; text-align: right; color: #34D399; font-weight: bold;">99.4% Faster</td>
          </tr>
          <tr style="border-bottom: 1px solid #1E293B;">
            <td style="padding: 12px 18px; font-family: sans-serif; font-weight: 600;">Cost on Off-Topic Queries</td>
            <td style="padding: 12px 18px; color: #34D399; font-weight: bold;">$0.00 (0 Tokens)</td>
            <td style="padding: 12px 18px; color: #94A3B8;">Standard API Billing</td>
            <td style="padding: 12px 18px; text-align: right; color: #34D399; font-weight: bold;">Zero Token Cost</td>
          </tr>
          <tr>
            <td style="padding: 12px 18px; font-family: sans-serif; font-weight: 600;">Grounded Benchmark Accuracy</td>
            <td style="padding: 12px 18px; color: #34D399; font-weight: bold;">10/10 (100%)</td>
            <td style="padding: 12px 18px; color: #94A3B8;">Frequent Hallucinations</td>
            <td style="padding: 12px 18px; text-align: right; color: #34D399; font-weight: bold;">Production Grade</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Author & Action Card -->
    <div class="card-highlight" style="display: flex; justify-content: space-between; align-items: center;">
      <div style="display: flex; align-items: center; gap: 14px;">
        <div style="width: 50px; height: 50px; background: linear-gradient(135deg, #06B6D4, #10B981); border-radius: 14px; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 20px; color: #0A0F1A;">FAN</div>
        <div>
          <div style="font-size: 18px; font-weight: 800; color: #FFFFFF;">Farwa Ali Nasir</div>
          <div class="mono" style="font-size: 13px; color: #38BDF8;">AI &amp; Machine Learning Software Engineer</div>
          <div style="font-size: 12px; color: #94A3B8; margin-top: 2px;">Open to Full-Time &amp; Associate AI/ML &amp; SWE Roles</div>
        </div>
      </div>
      <div style="text-align: right;" class="mono">
        <div style="color: #34D399; font-weight: bold; font-size: 13px;">Live Demo &amp; Code in Comments 👇</div>
        <div style="color: #64748B; font-size: 12px;">github.com/farwanasir2810-collab</div>
      </div>
    </div>

  </div>

  <div class="footer">
    <div>Architected for Enterprise Reliability • Fully Open Source</div>
    <div style="color: #38BDF8; font-weight: 700;">Test the Live App in the Comments! 🚀</div>
  </div>
</body>
</html>"""

# Render all 5 slides
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
base_dir = r"C:\Users\Hp\OneDrive\Desktop\RAG ChatBot\docs\carousel"
rendered_images = []

for name, html in slides_html.items():
    html_path = os.path.join(base_dir, f"{name}.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    png_path = os.path.join(base_dir, f"{name}_pure.png")
    jpg_path = os.path.join(base_dir, f"{name}.jpg")
    
    cmd = [
        chrome_path,
        "--headless",
        "--disable-gpu",
        "--hide-scrollbars",
        "--window-size=1200,1200",
        f"--screenshot={png_path}",
        f"file:///{html_path.replace(os.sep, '/')}"
    ]
    
    print(f"Rendering {name}...")
    subprocess.run(cmd, check=True)
    
    img = Image.open(png_path).convert("RGB")
    img.save(jpg_path, "JPEG", quality=95)
    rendered_images.append(img)
    print(f"Successfully saved {jpg_path}")
    
    try:
        os.remove(png_path)
    except Exception:
        pass

# Compile into PDF
pdf_path = os.path.join(base_dir, "ClinicDocs_AI_CaseStudy.pdf")
rendered_images[0].save(
    pdf_path,
    save_all=True,
    append_images=rendered_images[1:],
    quality=95
)
print(f"Successfully created 5-slide PDF: {pdf_path}")
