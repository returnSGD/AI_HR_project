<template>
  <div class="jdm">
    <div class="jdm-hdr">
      <h2 class="jdm-title">{{ t('jdm.title') }}</h2>
      <p class="jdm-sub">{{ t('jdm.sub') }}</p>
    </div>

    <div v-if="err" class="err">⚠️ {{ err }}</div>

    <div class="jdm-body">
      <!-- ── 左栏：JD 输入 ── -->
      <div class="col col-jd">
        <div class="col-label">
          <span class="col-icon">📋</span>
          {{ t('jdm.jdLabel') }}
        </div>
        <div class="jd-box" :class="{ focused: jdFocused, filled: jdText.length > 0 }">
          <textarea
            class="jd-ta"
            v-model="jdText"
            :placeholder="t('jdm.jdPh')"
            @focus="jdFocused = true"
            @blur="jdFocused = false"
          />
          <div class="jd-footer">
            <span class="jd-count" :class="{ warn: jdText.length > 2800 }">
              {{ jdText.length }} / 3000
            </span>
            <button v-if="jdText" class="jd-clear" @click="jdText = ''">
              {{ t('jdm.clear') }}
            </button>
          </div>
        </div>
      </div>

      <!-- ── 右栏：简历上传 + 结果 ── -->
      <div class="col col-right">
        <div class="col-label">
          <span class="col-icon">📄</span>
          {{ t('jdm.resumeLabel') }}
        </div>

        <label class="upload" :class="{ 'has-file': file }">
          <input
            type="file"
            accept=".pdf,.docx,.doc,.xlsx,.xls,.md,.txt,.jpg,.jpeg,.png"
            @change="pick"
            hidden
          />
          <span v-if="!file">{{ t('jdm.uploadHint') }}</span>
          <span v-else class="file-name">📄 {{ file.name }}</span>
        </label>

        <div class="analyze-row">
          <button
            class="btn analyze-btn"
            :disabled="!canAnalyze || phase === 'loading' || phase === 'streaming'"
            @click="analyze"
          >
            {{ phase === 'loading' || phase === 'streaming' ? t('jdm.analyzing') : t('jdm.analyzeBtn') }}
          </button>
          <span v-if="!canAnalyze && !phase.match(/loading|streaming/)" class="req-hint">
            {{ t('jdm.requireBoth') }}
          </span>
        </div>

        <div v-if="phase === 'loading'" class="status">⏳ {{ statusText }}</div>

        <!-- 流式结果 -->
        <transition name="result-fade">
          <div v-if="result" class="result-box rbox" v-html="renderedResult" />
        </transition>

        <div v-if="phase === 'done'" class="done-row">
          <button class="btn-g" @click="resetRight">{{ t('jdm.reset') }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'

const API_BASE = 'https://offer-catcher-api.onrender.com'
const { t, locale } = useI18n()

const jdText   = ref('')
const jdFocused= ref(false)
const file     = ref(null)
const phase    = ref('idle')   // idle | loading | streaming | done
const statusText = ref('')
const result   = ref('')
const err      = ref('')

const canAnalyze = computed(() => jdText.value.trim().length >= 20 && file.value)

const ALLOWED_EXTS = new Set(['pdf','docx','doc','xlsx','xls','md','txt','jpg','jpeg','png'])
function pick(e) {
  const f = e.target.files?.[0]
  if (!f) return
  const ext = f.name.split('.').pop().toLowerCase()
  if (ALLOWED_EXTS.has(ext)) { file.value = f; err.value = '' }
  else err.value = t('error.fileType')
}

async function analyze() {
  if (!canAnalyze.value) return
  err.value = ''; result.value = ''; phase.value = 'loading'
  statusText.value = locale.value === 'zh' ? '正在深度分析匹配度…' : 'Analyzing fit…'

  try {
    const fd = new FormData()
    fd.append('file', file.value)
    fd.append('jd_text', jdText.value.slice(0, 3000))

    const resp = await fetch(`${API_BASE}/api/analyze-jd`, {
      method: 'POST',
      headers: { 'Accept-Language': locale.value === 'zh' ? 'zh-CN' : 'en-US' },
      body: fd,
    })
    if (!resp.ok) {
      const e = await resp.json().catch(() => ({}))
      throw new Error(e.detail || `HTTP ${resp.status}`)
    }

    const reader = resp.body.getReader()
    const dec = new TextDecoder()
    let buf = ''
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buf += dec.decode(value, { stream: true })
      const lines = buf.split('\n'); buf = lines.pop() || ''
      for (const line of lines) {
        if (!line.startsWith('data: ')) continue
        const obj = JSON.parse(line.slice(6))
        if (obj.type === 'status') { statusText.value = obj.text; phase.value = 'loading' }
        else if (obj.type === 'chunk') { result.value += obj.text; phase.value = 'streaming' }
        else if (obj.type === 'error') throw new Error(obj.message)
        else if (obj.type === 'done') phase.value = 'done'
      }
    }
    phase.value = 'done'
  } catch (e) {
    err.value = e.message || t('error.api')
    phase.value = 'idle'
  }
}

function resetRight() {
  file.value = null; result.value = ''; phase.value = 'idle'; err.value = ''
}

// ── Markdown renderer (reuse same logic as App.vue) ──────────────
const renderedResult = computed(() => renderMarkdown(result.value))

function renderMarkdown(md) {
  const lines = md.split('\n')
  let html = '', ul = false, tbuf = []
  const inl = s => s.replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>').replace(/\*(.+?)\*/g,'<em>$1</em>')
  const flushTable = () => {
    if (tbuf.length < 2) { tbuf.forEach(l => { html += '<p>' + inl(l) + '</p>' }); tbuf = []; return }
    const cells = row => row.split('|').slice(1,-1).map(c=>c.trim())
    const heads = cells(tbuf[0])
    html += '<div class="tbl-wrap"><table class="md-tbl"><thead><tr>'
    heads.forEach(h => { html += `<th>${inl(h)}</th>` })
    html += '</tr></thead><tbody>'
    tbuf.slice(2).forEach(row => { html += '<tr>'; cells(row).forEach(c=>{ html+=`<td>${inl(c)}</td>` }); html+='</tr>' })
    html += '</tbody></table></div>'; tbuf = []
  }
  for (const raw of lines) {
    const t2 = raw.trim()
    if (t2.startsWith('|')) { if (ul){html+='</ul>';ul=false} tbuf.push(t2); continue }
    if (tbuf.length) flushTable()
    if (!t2) { if (ul){html+='</ul>';ul=false} continue }
    if (t2.startsWith('### ')) { if(ul){html+='</ul>';ul=false} html+='<h3>'+inl(t2.slice(4))+'</h3>'; continue }
    if (t2.startsWith('## '))  { if(ul){html+='</ul>';ul=false} html+='<h2>'+inl(t2.slice(3))+'</h2>'; continue }
    if (t2.startsWith('> '))   { if(ul){html+='</ul>';ul=false} html+='<blockquote>'+inl(t2.slice(2))+'</blockquote>'; continue }
    if (t2.startsWith('- '))   { if(!ul){html+='<ul>';ul=true}  html+='<li>'+inl(t2.slice(2))+'</li>'; continue }
    const m = t2.match(/^(\d+)\.\s(.*)/)
    if (m) { if(ul){html+='</ul>';ul=false} html+='<p><strong>'+m[1]+'.</strong> '+inl(m[2])+'</p>'; continue }
    if (ul){html+='</ul>';ul=false}
    html += '<p>'+inl(t2)+'</p>'
  }
  if (tbuf.length) flushTable()
  if (ul) html += '</ul>'
  return html
}
</script>

<style scoped>
.jdm { padding: 40px 20px 80px; max-width: 1100px; margin: 0 auto; }

.jdm-hdr { margin-bottom: 28px; }
.jdm-title { font-size: 1.4rem; font-weight: 800; letter-spacing: -.02em; margin-bottom: 6px; }
.jdm-sub   { font-size: .85rem; color: var(--g5); }

/* ── Two-column grid ── */
.jdm-body {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  align-items: start;
}
@media (max-width: 680px) { .jdm-body { grid-template-columns: 1fr; } }

/* ── Column labels ── */
.col-label {
  display: flex; align-items: center; gap: 7px;
  font-size: .78rem; font-weight: 700; letter-spacing: .02em; text-transform: uppercase;
  color: var(--g5); margin-bottom: 10px;
}
.col-icon { font-size: 1rem; }

/* ── JD textarea box ── */
.jd-box {
  border: 1.5px solid rgba(0,0,0,.1);
  border-radius: 18px;
  background: rgba(255,255,255,.9);
  transition: border-color .35s var(--ease), box-shadow .35s var(--ease);
  overflow: hidden;
}
.jd-box.focused {
  border-color: var(--y);
  box-shadow: 0 0 0 3px rgba(245,166,35,.13);
}
.jd-ta {
  width: 100%; min-height: 320px;
  border: none; outline: none; resize: none;
  padding: 16px 18px;
  font-size: .88rem; line-height: 1.7;
  font-family: inherit;
  background: transparent;
  color: var(--dk);
}
.jd-ta::placeholder { color: #94a3b8; }
.jd-footer {
  display: flex; align-items: center; justify-content: space-between;
  padding: 8px 14px;
  border-top: 1px solid rgba(0,0,0,.05);
  background: rgba(0,0,0,.02);
}
.jd-count { font-size: .7rem; color: var(--g5); font-variant-numeric: tabular-nums; }
.jd-count.warn { color: #ef4444; }
.jd-clear {
  font-size: .72rem; font-weight: 600; color: var(--g5);
  background: none; border: none; cursor: pointer; padding: 2px 6px;
  border-radius: 6px; transition: background .2s var(--ease), color .2s var(--ease);
}
.jd-clear:hover { background: rgba(0,0,0,.06); color: var(--dk); }

/* ── Right column ── */
.col-right { display: flex; flex-direction: column; gap: 14px; }

.upload {
  display: block; border: 2px dashed rgba(0,0,0,.11);
  border-radius: 18px; background: rgba(255,255,255,.75);
  padding: 36px 32px; text-align: center;
  cursor: pointer; font-weight: 600; font-size: .9rem;
  transition: border-color .4s var(--ease), background .4s var(--ease), transform .5s var(--ease);
}
.upload:hover {
  border-color: rgba(245,166,35,.5); background: rgba(255,248,230,.9);
  transform: scale(1.012) translateY(-2px);
}
.upload.has-file { border-style: solid; border-color: rgba(245,166,35,.4); background: rgba(255,248,230,.6); }
.file-name { color: var(--dk); }

/* ── Analyze button row ── */
.analyze-row { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.analyze-btn { flex-shrink: 0; }
.req-hint { font-size: .74rem; color: var(--g5); }

/* ── Status / error ── */
.status {
  background: rgba(255,248,230,.92); border: 1.5px solid rgba(245,166,35,.22);
  border-radius: 14px; padding: 12px 18px; color: #78350F; font-size: .86rem;
  animation: fadeUp .4s var(--ease);
}
.err {
  background: rgba(254,242,242,.92); border: 1.5px solid rgba(252,165,165,.4);
  border-radius: 14px; padding: 12px 18px; color: #991B1B; margin-bottom: 14px;
  animation: fadeUp .4s var(--ease);
}

/* ── Result box ── */
.result-box { animation: none !important; }
.result-fade-enter-active { transition: opacity .55s var(--ease), transform .55s var(--ease); }
.result-fade-enter-from   { opacity: 0; transform: translateY(12px); }

/* Inherit rbox styles from global, add section heading styles */
:deep(.result-box h2) {
  font-size: .92rem; margin: 20px 0 8px;
  padding-bottom: 5px; border-bottom: 2px solid var(--y-soft);
  letter-spacing: -.01em;
}
:deep(.result-box h2:first-child) { margin-top: 0; }
:deep(.result-box h3) { font-size: .87rem; font-weight: 700; margin: 10px 0 4px; }
:deep(.result-box p), :deep(.result-box li) { font-size: .84rem; line-height: 1.75; }
:deep(.result-box ul) { padding-left: 20px; }
:deep(.result-box blockquote) {
  border-left: 3px solid var(--y); margin: 6px 0;
  padding: 5px 14px; background: var(--y-soft); border-radius: 0 8px 8px 0; font-size: .83rem;
}

.done-row { text-align: right; }
</style>
