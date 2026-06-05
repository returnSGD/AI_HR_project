<template>
  <header class="hdr">
    <div class="logo"><span class="lb">🎯</span> Offer-Catcher <span class="pill">{{ t('badge') }}</span></div>
    <div class="hr">
      <button v-if="phase === 'done'" class="btn-g" @click="reset">{{ t('nav.new') }}</button>
      <button class="prof" @click="showProfile = true" :title="t('nav.profile')">👤</button>
    </div>
  </header>

  <!-- Toast -->
  <Transition name="toast">
    <div v-if="toast" class="toast">{{ toast }}</div>
  </Transition>

  <main class="main">
    <div v-if="err" class="err">⚠️ {{ err }}</div>

    <!-- ── SEEKER MODE ──────────────────────────────────────── -->
    <template v-if="mode === 'seeker'">
      <template v-if="phase === 'idle'">
        <h1 v-if="locale === 'zh'" class="h1">{{ t('hero.l1') }}<br><span class="ac">{{ t('hero.accent') }}</span></h1>
        <h1 v-else class="h1">{{ t('hero.l1') }} <span class="ac">{{ t('hero.accent') }}</span><br>{{ t('hero.l2') }}</h1>
        <p class="sub">{{ t('hero.sub') }}</p>

        <label class="upload">
          <input type="file" accept=".pdf,.docx,.doc,.xlsx,.xls,.md,.txt,.jpg,.jpeg,.png" @change="pick" hidden>
          <span v-if="!file">📋 {{ t('upload.drag') }}</span>
          <span v-else>📄 {{ file.name }}</span>
        </label>

        <!-- Job preference filters -->
        <div class="filter-row">
          <!-- Level 1: Province -->
          <div class="filter-chip">
            <span class="flt-lbl">🗺 {{ t('filter.province') }}</span>
            <select v-model="filters.province" class="flt-sel">
              <option value="">{{ t('filter.all') }}</option>
              <option v-for="p in PROVINCE_LIST" :key="p" :value="p">{{ p }}</option>
            </select>
          </div>
          <!-- Level 2: City — only visible after province selected, hidden for single-city provinces -->
          <div class="filter-chip" v-if="filters.province && provinceCities.length > 1">
            <span class="flt-lbl">🏙 {{ t('filter.city') }}</span>
            <select v-model="filters.city" class="flt-sel">
              <option value="">{{ t('filter.allCity') }}</option>
              <option v-for="c in provinceCities" :key="c" :value="c">{{ c }}</option>
            </select>
          </div>
          <div class="filter-chip">
            <span class="flt-lbl">💼 {{ t('filter.type') }}</span>
            <select v-model="filters.jobType" class="flt-sel">
              <option value="">{{ t('filter.all') }}</option>
              <option value="实习">{{ t('filter.intern') }}</option>
              <option value="校招">{{ t('filter.campus') }}</option>
              <option value="全职">{{ t('filter.fulltime') }}</option>
            </select>
          </div>
        </div>

        <div class="center">
          <button class="btn" :disabled="!file" @click="run">{{ t('btn.run') }}</button>
        </div>
      </template>

      <template v-else>
        <div v-if="phase === 'loading'" class="status">⏳ {{ statusText }}</div>

        <div v-if="jobs.length">
          <div class="slabel">
            {{ t('section.jobs', { n: displayJobs.length }) }}
            <span v-if="liveCount > 0" class="live-badge">🌐 {{ liveCount }} {{ t('section.liveJobs') }}</span>
          </div>
          <div class="match-note">ℹ️ {{ t('section.matchNote') }}</div>
          <div
            v-for="(j, i) in displayJobs" :key="j.id"
            :class="['job', i === 0 && 'top']"
            @click="expandedId = expandedId === j.id ? null : j.id"
          >
            <div class="job-top">
              <div>
                <div class="co">{{ j.company }}</div>
                <div class="ti">{{ j.title }}</div>
              </div>
              <div class="job-right">
                <!-- Source tag: crawled with valid URL → clickable <a>; otherwise plain <span> -->
                <a
                  v-if="j.source_type === 'crawled' && j.url"
                  :href="j.url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="src-tag src-crawled src-link"
                  @click.stop
                >🌐 {{ j.platform || t('source.crawled').replace('🌐 ', '') }}</a>
                <span
                  v-else-if="j.source_type === 'crawled'"
                  class="src-tag src-crawled"
                >🌐 {{ j.platform || t('source.crawled').replace('🌐 ', '') }}</span>
                <span
                  v-else
                  :class="['src-tag', `src-${j.source_type || 'preset'}`]"
                >{{ t(`source.${j.source_type || 'preset'}`) }}</span>
                <div class="score" :title="t('job.matchTip')">{{ j.score }}%<span>{{ t('job.match') }} ℹ️</span></div>
              </div>
            </div>
            <div class="tags"><span v-for="tg in j.tags" :key="tg">{{ tg }}</span></div>
            <div v-if="j.created_at" class="job-date">{{ t('job.posted') }} {{ j.created_at }}</div>

            <!-- Expandable JD detail -->
            <div v-if="expandedId === j.id" class="job-detail">
              <!-- Meta row -->
              <div class="jd-meta">
                <span class="jd-meta-item">📍 <strong>{{ j.location || '—' }}</strong></span>
                <span class="jd-meta-item">💰 <strong>{{ j.salary || '—' }}</strong></span>
                <span class="jd-meta-item">💼 <strong>{{ j.type || '—' }}</strong></span>
                <span v-if="j.created_at" class="jd-meta-item">📅 <strong>{{ j.created_at }}</strong></span>
              </div>

              <!-- Skill gap visualization -->
              <div v-if="j.matched_kws?.length" class="gap-row">
                <span class="gap-label gap-match">✅ {{ t('job.matchedSkills') }}</span>
                <span v-for="kw in j.matched_kws.slice(0,7)" :key="kw" class="kw-chip kw-match">{{ kw }}</span>
              </div>
              <div v-if="j.missing_kws?.length" class="gap-row">
                <span class="gap-label gap-miss">❌ {{ t('job.missingSkills') }}</span>
                <span v-for="kw in j.missing_kws.slice(0,7)" :key="kw" class="kw-chip kw-miss">{{ kw }}</span>
              </div>

              <!-- Full JD -->
              <div v-if="loadingJd[j.id]" class="jd-loading">⏳ {{ t('job.loadingJd') }}</div>
              <div v-else-if="jobJds[j.id]" class="jd-full rbox" v-html="renderMarkdown(jobJds[j.id])"></div>
              <p v-else-if="j.description" class="jd-desc">{{ j.description }}</p>

              <a v-if="j.url" :href="j.url" target="_blank" rel="noopener noreferrer" class="jd-apply" @click.stop>{{ t('job.apply') }} ↗</a>

              <!-- Optimize button + streaming result -->
              <!-- Resume optimize button -->
              <button
                v-if="file"
                class="opt-btn"
                :disabled="!!optimizing[j.id]"
                @click.stop="optimizeForJob(j)"
              >{{ optimizing[j.id] ? t('job.optimizing') : t('job.optimizeBtn') }}</button>
              <div v-if="optimizeResult[j.id]" class="opt-result rbox" v-html="renderMarkdown(optimizeResult[j.id])"></div>

              <!-- HR perspective simulation button -->
              <button
                v-if="file"
                class="hr-btn"
                :disabled="!!hrViewing[j.id]"
                @click.stop="hrViewResume(j)"
              >{{ hrViewing[j.id] ? t('job.hrViewing') : t('job.hrBtn') }}</button>
              <div v-if="hrResult[j.id]" class="hr-result" v-html="renderMarkdown(hrResult[j.id])"></div>
            </div>

            <div class="job-expand-hint">{{ expandedId === j.id ? '▲' : '▼' }}</div>
          </div>
        </div>

        <div v-if="report" class="slabel">
          {{ t('section.report') }}
          <span class="bdg">{{ phase === 'done' ? t('section.complete') : t('section.generating') }}</span>
        </div>
        <div v-if="report" class="rbox" v-html="reportHtml"></div>

        <div v-if="phase === 'done'" class="center">
          <button class="btn" @click="reset">{{ t('btn.again') }}</button>
        </div>
      </template>
    </template>

    <!-- ── RECRUITER MODE ───────────────────────────────────── -->
    <template v-else>
      <h2 class="rec-title">{{ t('recruiter.title') }}</h2>

      <div class="form">
        <div class="row2">
          <div class="field">
            <label>{{ t('recruiter.company') }} <span class="req">*</span></label>
            <input v-model="jd.company" :placeholder="t('recruiter.companyPh')" class="inp" />
          </div>
          <div class="field">
            <label>{{ t('recruiter.jobTitle') }} <span class="req">*</span></label>
            <input v-model="jd.title" :placeholder="t('recruiter.jobTitlePh')" class="inp" />
          </div>
        </div>
        <div class="row2">
          <div class="field">
            <label>{{ t('recruiter.salary') }}</label>
            <input v-model="jd.salary" :placeholder="t('recruiter.salaryPh')" class="inp" />
          </div>
          <div class="field">
            <label>{{ t('recruiter.location') }}</label>
            <input v-model="jd.location" :placeholder="t('recruiter.locationPh')" class="inp" />
          </div>
        </div>
        <div class="field">
          <label>{{ t('recruiter.tags') }}</label>
          <input v-model="jd.tagsRaw" :placeholder="t('recruiter.tagsPh')" class="inp" />
        </div>
        <div class="field">
          <label>{{ t('recruiter.desc') }}</label>
          <div class="ta-wrap">
            <textarea v-model="jd.description" :placeholder="t('recruiter.descPh')" class="ta" rows="6" />
            <button class="ai-btn" :disabled="aiLoading" @click="aiPolish">
              {{ aiLoading ? t('recruiter.aiLoading') : t('recruiter.aiBtn') }}
            </button>
          </div>
        </div>
        <div class="center">
          <button class="btn" :disabled="publishing" @click="publish">
            {{ publishing ? '…' : t('recruiter.submit') }}
          </button>
        </div>
      </div>
    </template>

    <div class="footer">{{ t('footer') }}</div>
  </main>

  <!-- Profile panel -->
  <Transition name="slide">
    <div v-if="showProfile" class="overlay" @click.self="showProfile = false">
      <div class="panel">
        <div class="panel-hdr">
          <span class="panel-title">{{ t('profile.title') }}</span>
          <button class="close" @click="showProfile = false">✕</button>
        </div>
        <div class="avatar">👤</div>
        <div class="uname">{{ t('profile.guest') }}</div>
        <div class="usub">{{ t('profile.guestSub') }}</div>

        <!-- Mode toggle -->
        <div class="toggle-row">
          <span :class="['tog-lbl', mode === 'seeker' && 'tog-active']">{{ t('mode.seeker') }}</span>
          <button class="tog" :class="{ 'tog-on': mode === 'recruiter' }" @click="toggleMode">
            <span class="tog-thumb" />
          </button>
          <span :class="['tog-lbl', mode === 'recruiter' && 'tog-active']">{{ t('mode.recruiter') }}</span>
        </div>

        <div class="divider" />
        <div class="prow"><span>{{ t('profile.langLabel') }}</span>
          <select class="sel" @change="e => { setLocale(e.target.value) }">
            <option value="zh" :selected="locale === 'zh'">中文</option>
            <option value="en" :selected="locale === 'en'">English</option>
          </select>
        </div>

        <!-- Preset visibility toggle -->
        <div class="divider" />
        <div class="prow">
          <span>{{ t('profile.showPreset') }}</span>
          <button class="tog" :class="{ 'tog-on': showPreset }" @click="togglePreset">
            <span class="tog-thumb" />
          </button>
        </div>

        <!-- Recruiter: my posted jobs -->
        <template v-if="mode === 'recruiter' && myPostedJobs.length">
          <div class="divider" />
          <div class="about-title">{{ t('profile.myJobs') }}</div>
          <div v-for="pj in myPostedJobs" :key="pj.id" class="my-job-row">
            <div class="my-job-info">
              <span class="my-job-title">{{ pj.title }}</span>
              <span :class="['my-job-status', pj.is_active ? 'status-active' : 'status-closed']">
                {{ pj.is_active ? t('profile.jobActive') : t('profile.jobClosed') }}
              </span>
            </div>
            <div class="my-job-meta">{{ pj.company }} · {{ pj.created_at || '' }}</div>
            <div class="my-job-actions">
              <button v-if="pj.is_active" class="btn-sm btn-close" @click="closeJob(pj.id)">
                {{ t('profile.closeJob') }}
              </button>
              <button v-else class="btn-sm btn-reopen" @click="reopenJob(pj.id)">
                {{ t('profile.reopenJob') }}
              </button>
            </div>
          </div>
        </template>

        <div class="divider" />
        <div class="about-title">{{ t('profile.about') }}</div>
        <div class="about-desc">{{ t('profile.aboutDesc') }}</div>
        <div class="ver">{{ t('profile.version') }}</div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { setLocale } from './i18n.js'
import { CHINA_CITY_GROUPS } from './cities.js'

const API_BASE = 'https://offer-catcher-api.onrender.com'
const { t, locale } = useI18n()

// ── Global state ──────────────────────────────────────────────────────
const mode        = ref(localStorage.getItem('oc_mode') || 'seeker') // 'seeker' | 'recruiter'
const showProfile = ref(false)
const toast       = ref('')
let   toastTimer  = null

function showToast(msg) {
  toast.value = msg
  clearTimeout(toastTimer)
  toastTimer = setTimeout(() => { toast.value = '' }, 2800)
}

function toggleMode() {
  mode.value = mode.value === 'seeker' ? 'recruiter' : 'seeker'
  localStorage.setItem('oc_mode', mode.value)
  showProfile.value = false
}

// Province list and map derived from imported CHINA_CITY_GROUPS
const PROVINCE_LIST   = CHINA_CITY_GROUPS.map(g => g.label)
const PROVINCE_CITIES = Object.fromEntries(CHINA_CITY_GROUPS.map(g => [g.label, g.cities]))

// ── Preset-visibility setting ─────────────────────────────────────────
const showPreset = ref(localStorage.getItem('oc_show_preset') !== 'false')
function togglePreset() {
  showPreset.value = !showPreset.value
  localStorage.setItem('oc_show_preset', showPreset.value)
}

// ── Seeker state ──────────────────────────────────────────────────────
const phase      = ref('idle')
const file       = ref(null)
const filters    = ref({ province: '', city: '', jobType: '' })

// Reset city when province changes
watch(() => filters.value.province, () => { filters.value.city = '' })

// Cities available for selected province
const provinceCities = computed(() => PROVINCE_CITIES[filters.value.province] || [])
const expandedId    = ref(null)
const liveCount     = ref(0)
const optimizing     = ref({})
const optimizeResult = ref({})
const hrViewing      = ref({})
const hrResult       = ref({})
const jobJds       = ref({})   // id → full JD string (cached)
const loadingJd    = ref({})   // id → boolean
const jobs         = ref([])
const report       = ref('')
const err          = ref('')
const statusText   = ref('')

// Lazy-load full JD when a card is expanded
watch(expandedId, async (id) => {
  if (!id || jobJds.value[id]) return
  loadingJd.value = { ...loadingJd.value, [id]: true }
  try {
    const resp = await fetch(`${API_BASE}/api/jobs/${id}/jd`)
    if (resp.ok) {
      const data = await resp.json()
      jobJds.value = { ...jobJds.value, [id]: data.jd }
    }
  } catch (_) { /* silently fall back to short description */ }
  finally {
    loadingJd.value = { ...loadingJd.value, [id]: false }
  }
})

// Filter out preset jobs when toggle is off
const displayJobs = computed(() =>
  showPreset.value ? jobs.value : jobs.value.filter(j => j.source_type !== 'preset')
)

const reportHtml = computed(() => renderMarkdown(report.value))

function renderMarkdown(md) {
  const lines = md.split('\n')
  let html = '', ul = false, tbuf = []

  const inl = s => s
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')

  const flushTable = () => {
    if (tbuf.length < 2) { tbuf.forEach(l => { html += '<p>' + inl(l) + '</p>' }); tbuf = []; return }
    const cells = row => row.split('|').slice(1, -1).map(c => c.trim())
    const heads = cells(tbuf[0])
    html += '<div class="tbl-wrap"><table class="md-tbl"><thead><tr>'
    heads.forEach(h => { html += `<th>${inl(h)}</th>` })
    html += '</tr></thead><tbody>'
    tbuf.slice(2).forEach(row => {
      html += '<tr>'
      cells(row).forEach(c => { html += `<td>${inl(c)}</td>` })
      html += '</tr>'
    })
    html += '</tbody></table></div>'
    tbuf = []
  }

  for (const raw of lines) {
    const t = raw.trim()
    if (t.startsWith('|')) {
      if (ul) { html += '</ul>'; ul = false }
      tbuf.push(t); continue
    }
    if (tbuf.length) flushTable()
    if (!t) { if (ul) { html += '</ul>'; ul = false } continue }
    if (t.startsWith('### ')) { if (ul) { html += '</ul>'; ul = false } html += '<h3>' + inl(t.slice(4)) + '</h3>'; continue }
    if (t.startsWith('## '))  { if (ul) { html += '</ul>'; ul = false } html += '<h2>' + inl(t.slice(3)) + '</h2>'; continue }
    if (t.startsWith('> '))   { if (ul) { html += '</ul>'; ul = false } html += '<blockquote>' + inl(t.slice(2)) + '</blockquote>'; continue }
    if (t.startsWith('- '))   { if (!ul) { html += '<ul>'; ul = true } html += '<li>' + inl(t.slice(2)) + '</li>'; continue }
    const m = t.match(/^(\d+)\.\s(.*)/)
    if (m) { if (ul) { html += '</ul>'; ul = false } html += '<p><strong>' + m[1] + '.</strong> ' + inl(m[2]) + '</p>'; continue }
    if (ul) { html += '</ul>'; ul = false }
    html += '<p>' + inl(t) + '</p>'
  }
  if (tbuf.length) flushTable()
  if (ul) html += '</ul>'
  return html
}

const ALLOWED_EXTS = new Set(['pdf','docx','doc','xlsx','xls','md','txt','jpg','jpeg','png'])
const ALLOWED_MIME = new Set([
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'application/vnd.ms-excel',
  'text/plain', 'text/markdown',
  'image/jpeg', 'image/png',
])

function pick(e) {
  const f = e.target.files?.[0]
  if (!f) return
  const ext = f.name.split('.').pop().toLowerCase()
  if (ALLOWED_MIME.has(f.type) || ALLOWED_EXTS.has(ext)) {
    file.value = f; err.value = ''
  } else {
    err.value = t('error.fileType')
  }
}

async function run() {
  if (!file.value) return
  err.value = ''; jobs.value = []; report.value = ''
  phase.value = 'loading'; statusText.value = t('status.read')
  try {
    const fd = new FormData()
    fd.append('file', file.value)
    // Only send city when a specific city (not just province) is selected
    const cityVal = filters.value.city || (provinceCities.value.length === 1 ? provinceCities.value[0] : '')
    if (cityVal) fd.append('preferred_city', cityVal)
    if (filters.value.jobType) fd.append('preferred_type', filters.value.jobType)
    const resp = await fetch(`${API_BASE}/api/match`, {
      method: 'POST',
      headers: { 'Accept-Language': locale.value === 'zh' ? 'zh-CN' : 'en-US' },
      body: fd
    })
    if (!resp.ok) {
      const e = await resp.json().catch(() => ({}))
      throw new Error(e.detail || ('HTTP ' + resp.status))
    }
    statusText.value = t('status.match')
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
        if (obj.type === 'status') { statusText.value = obj.text }
        else if (obj.type === 'jobs') {
          jobs.value = obj.jobs
          liveCount.value = obj.live_count || 0
          phase.value = 'streaming'
        }
        else if (obj.type === 'chunk') { report.value += obj.text }
        else if (obj.type === 'error') { throw new Error(obj.message) }
        else if (obj.type === 'done') { phase.value = 'done' }
      }
    }
    phase.value = 'done'
  } catch (e) {
    err.value = e.message || t('error.api')
    phase.value = 'idle'
  }
}

function reset() {
  phase.value = 'idle'; file.value = null; jobs.value = []
  report.value = ''; err.value = ''; expandedId.value = null
  liveCount.value = 0
  optimizing.value = {}; optimizeResult.value = {}
  hrViewing.value = {}; hrResult.value = {}
  filters.value.province = ''; filters.value.city = ''
}

async function hrViewResume(job) {
  if (!file.value) return
  hrViewing.value  = { ...hrViewing.value,  [job.id]: true }
  hrResult.value   = { ...hrResult.value,   [job.id]: '' }
  try {
    const fd = new FormData()
    fd.append('file', file.value)
    const resp = await fetch(`${API_BASE}/api/jobs/${job.id}/hr-view`, {
      method: 'POST',
      headers: { 'Accept-Language': locale.value === 'zh' ? 'zh-CN' : 'en-US' },
      body: fd,
    })
    if (!resp.ok) throw new Error('HTTP ' + resp.status)
    const reader = resp.body.getReader()
    const dec    = new TextDecoder()
    let   text   = ''
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      text += dec.decode(value, { stream: true })
      hrResult.value = { ...hrResult.value, [job.id]: text }
    }
  } catch (e) {
    hrResult.value = { ...hrResult.value, [job.id]: `> ❌ ${e.message}` }
  } finally {
    hrViewing.value = { ...hrViewing.value, [job.id]: false }
  }
}

async function optimizeForJob(job) {
  if (!file.value) return
  optimizing.value  = { ...optimizing.value,    [job.id]: true  }
  optimizeResult.value = { ...optimizeResult.value, [job.id]: ''  }
  try {
    const fd = new FormData()
    fd.append('file', file.value)
    const resp = await fetch(`${API_BASE}/api/jobs/${job.id}/optimize`, {
      method: 'POST',
      headers: { 'Accept-Language': locale.value === 'zh' ? 'zh-CN' : 'en-US' },
      body: fd,
    })
    if (!resp.ok) throw new Error('HTTP ' + resp.status)
    const reader = resp.body.getReader()
    const dec    = new TextDecoder()
    let   text   = ''
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      text += dec.decode(value, { stream: true })
      optimizeResult.value = { ...optimizeResult.value, [job.id]: text }
    }
  } catch (e) {
    optimizeResult.value = { ...optimizeResult.value, [job.id]: `> ❌ ${e.message}` }
  } finally {
    optimizing.value = { ...optimizing.value, [job.id]: false }
  }
}

// ── Recruiter state ───────────────────────────────────────────────────
const jd = ref({ company: '', title: '', salary: '', location: '', tagsRaw: '', description: '' })
const aiLoading  = ref(false)
const publishing = ref(false)
// Track posted jobs (full objects) in localStorage
const myPostedJobs = ref(JSON.parse(localStorage.getItem('oc_my_jobs') || '[]'))

async function aiPolish() {
  if (!jd.value.description.trim()) return
  aiLoading.value = true
  err.value = ''
  try {
    const resp = await fetch(`${API_BASE}/api/generate-jd`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ raw_text: jd.value.description }),
    })
    if (!resp.ok) throw new Error('HTTP ' + resp.status)
    const data = await resp.json()
    jd.value.description = data.jd
  } catch (e) {
    err.value = e.message || t('error.api')
  } finally {
    aiLoading.value = false
  }
}

async function publish() {
  if (!jd.value.company.trim() || !jd.value.title.trim()) {
    err.value = t('recruiter.required'); return
  }
  publishing.value = true
  err.value = ''
  try {
    const tags = jd.value.tagsRaw.split(',').map(s => s.trim()).filter(Boolean)
    const resp = await fetch(`${API_BASE}/api/jobs`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...jd.value, tags, keywords: tags.map(t => t.toLowerCase()) }),
    })
    if (!resp.ok) throw new Error('HTTP ' + resp.status)
    const data = await resp.json()
    // Save full job object for recruiter management panel
    myPostedJobs.value = [data, ...myPostedJobs.value]
    localStorage.setItem('oc_my_jobs', JSON.stringify(myPostedJobs.value))
    jd.value = { company: '', title: '', salary: '', location: '', tagsRaw: '', description: '' }
    showToast(t('recruiter.toast'))
  } catch (e) {
    err.value = e.message || t('error.api')
  } finally {
    publishing.value = false
  }
}

async function closeJob(jobId) {
  try {
    await fetch(`${API_BASE}/api/jobs/${jobId}?is_active=0`, { method: 'PATCH' })
    myPostedJobs.value = myPostedJobs.value.map(j =>
      j.id === jobId ? { ...j, is_active: 0 } : j
    )
    localStorage.setItem('oc_my_jobs', JSON.stringify(myPostedJobs.value))
    showToast(t('recruiter.closedToast'))
  } catch (e) { err.value = e.message || t('error.api') }
}

async function reopenJob(jobId) {
  try {
    await fetch(`${API_BASE}/api/jobs/${jobId}?is_active=1`, { method: 'PATCH' })
    myPostedJobs.value = myPostedJobs.value.map(j =>
      j.id === jobId ? { ...j, is_active: 1 } : j
    )
    localStorage.setItem('oc_my_jobs', JSON.stringify(myPostedJobs.value))
    showToast(t('recruiter.reopenedToast'))
  } catch (e) { err.value = e.message || t('error.api') }
}
</script>

<style>
:root { --y: #FFD700; --yh: #F0C800; --dk: #0F172A; --g5: #64748B; --g2: #E2E8F0; --blue: #3B82F6; --green: #10B981; }
* { box-sizing: border-box; margin: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #F8FAFC; color: var(--dk); }

/* Header */
.hdr { background: #fff; border-bottom: 1px solid var(--g2); height: 58px; padding: 0 24px; display: flex; align-items: center; justify-content: space-between; }
.logo { font-weight: 800; }
.lb { background: var(--y); border-radius: 8px; padding: 4px 6px; }
.pill { font-size: .65rem; font-weight: 700; background: #FFFBEB; border: 1px solid #FDE68A; color: #92400E; padding: 2px 8px; border-radius: 20px; }
.hr { display: flex; align-items: center; gap: 8px; }
.prof { width: 34px; height: 34px; border-radius: 50%; border: 1.5px solid var(--g2); background: #fff; cursor: pointer; }
.prof:hover { border-color: var(--y); background: #FFFBEB; }

/* Toast */
.toast { position: fixed; top: 70px; left: 50%; transform: translateX(-50%); background: #0F172A; color: #fff; padding: 10px 22px; border-radius: 20px; font-size: .85rem; font-weight: 600; z-index: 1000; pointer-events: none; }
.toast-enter-active, .toast-leave-active { transition: opacity .25s, transform .25s; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateX(-50%) translateY(-8px); }

/* Main layout */
.main { max-width: 760px; margin: 0 auto; padding: 40px 20px 80px; }
.h1 { font-size: clamp(1.8rem, 5vw, 2.6rem); font-weight: 900; text-align: center; line-height: 1.15; }
.ac { color: var(--yh); }
.sub { text-align: center; color: var(--g5); margin: 14px auto 28px; max-width: 480px; }
.upload { display: block; border: 2px dashed var(--g2); border-radius: 14px; background: #fff; padding: 48px; text-align: center; cursor: pointer; font-weight: 600; }
.upload:hover { border-color: var(--y); background: #FFFBEB; }
.filter-row { display: flex; justify-content: center; gap: 16px; margin: 14px 0 4px; flex-wrap: wrap; }
.filter-chip { display: flex; align-items: center; gap: 7px; }
.flt-lbl { font-size: .8rem; color: var(--g5); font-weight: 600; }
.flt-sel { border: 1px solid var(--g2); border-radius: 20px; padding: 5px 12px; font-size: .82rem; background: #fff; cursor: pointer; appearance: none; -webkit-appearance: none; }
.flt-sel:focus { outline: none; border-color: var(--y); }
.center { text-align: center; margin-top: 20px; }
.btn { background: var(--y); border: none; border-radius: 8px; padding: 13px 32px; font-weight: 700; cursor: pointer; box-shadow: 0 2px 10px rgba(255,215,0,.35); }
.btn:hover:not([disabled]) { background: var(--yh); }
.btn[disabled] { opacity: .55; cursor: not-allowed; }
.btn-g { background: #fff; border: 1px solid var(--g2); border-radius: 8px; padding: 8px 16px; font-weight: 600; cursor: pointer; }
.status { background: #FFFBEB; border: 1px solid #FDE68A; border-radius: 8px; padding: 12px 18px; color: #78350F; margin-bottom: 20px; }
.err { background: #FEF2F2; border: 1px solid #FECACA; border-radius: 8px; padding: 14px 18px; color: #991B1B; margin-bottom: 20px; }
.slabel { font-weight: 700; margin: 22px 0 6px; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.match-note { font-size: .74rem; color: #94A3B8; margin-bottom: 14px; }
.live-badge { font-size: .68rem; font-weight: 700; background: #EFF6FF; border: 1px solid #BFDBFE; color: var(--blue); padding: 2px 9px; border-radius: 20px; }
.bdg { font-size: .68rem; font-weight: 700; background: #FFFBEB; border: 1px solid #FDE68A; color: #92400E; padding: 2px 8px; border-radius: 20px; }

/* Job card */
.job { background: #fff; border: 1px solid var(--g2); border-radius: 14px; padding: 18px; margin-bottom: 12px; cursor: pointer; position: relative; }
.job.top { border-top: 3px solid var(--y); }
.job:hover { border-color: #CBD5E1; }
.job-expand-hint { position: absolute; bottom: 10px; right: 14px; font-size: .65rem; color: #CBD5E1; }
.job-date { font-size: .72rem; color: #94A3B8; margin-top: 6px; }
.job-detail { border-top: 1px solid var(--g2); margin-top: 12px; padding-top: 12px; animation: jdIn .15s ease; }
.jd-meta { display: flex; flex-wrap: wrap; gap: 14px; margin-bottom: 10px; }
.jd-meta-item { font-size: .8rem; color: var(--g5); }
.jd-meta-item strong { color: var(--dk); font-weight: 600; }
.jd-desc { font-size: .83rem; color: #374151; line-height: 1.7; margin: 0 0 10px; }
.jd-apply { font-size: .78rem; font-weight: 700; color: var(--blue); text-decoration: none; display: inline-block; margin-top: 6px; }
.jd-apply:hover { text-decoration: underline; }
/* Skill gap */
.gap-row { display: flex; flex-wrap: wrap; gap: 5px; margin: 6px 0; align-items: center; }
.gap-label { font-size: .7rem; font-weight: 700; padding: 2px 7px; border-radius: 4px; white-space: nowrap; }
.gap-match { color: #059669; background: #ECFDF5; }
.gap-miss  { color: #DC2626; background: #FEF2F2; }
.kw-chip   { font-size: .7rem; padding: 2px 8px; border-radius: 10px; }
.kw-match  { background: #D1FAE5; color: #065F46; }
.kw-miss   { background: #FEE2E2; color: #991B1B; }
/* Optimize button */
.opt-btn  { margin-top: 12px; background: var(--dk); color: #fff; border: none; border-radius: 8px; padding: 8px 18px; font-size: .82rem; font-weight: 700; cursor: pointer; transition: opacity .15s; display: block; }
.opt-btn:hover:not([disabled]) { opacity: .8; }
.opt-btn[disabled] { opacity: .5; cursor: not-allowed; }
.opt-result { margin-top: 12px; }
.hr-btn  { margin-top: 10px; background: #7C3AED; color: #fff; border: none; border-radius: 8px; padding: 8px 18px; font-size: .82rem; font-weight: 700; cursor: pointer; transition: opacity .15s; display: block; }
.hr-btn:hover:not([disabled]) { opacity: .8; }
.hr-btn[disabled] { opacity: .5; cursor: not-allowed; }
.hr-result { margin-top: 12px; background: #FAF5FF; border: 1px solid #DDD6FE; border-radius: 12px; padding: 18px; line-height: 1.8; }
.hr-result h2 { font-size: .9rem; margin: 14px 0 6px; padding-bottom: 4px; border-bottom: 2px solid #EDE9FE; }
.hr-result h2:first-child { margin-top: 0; }
.hr-result blockquote { border-left: 3px solid #7C3AED; margin: 6px 0; padding: 4px 12px; background: #EDE9FE; border-radius: 0 6px 6px 0; font-style: italic; font-size: .84rem; }
.hr-result ul { padding-left: 20px; }
.hr-result p, .hr-result li { font-size: .84rem; }
.jd-loading { font-size: .82rem; color: var(--g5); padding: 10px 0; }
.jd-full { border: none; border-radius: 0; padding: 0; margin: 0; box-shadow: none; }
.jd-full h2 { font-size: .9rem; margin: 16px 0 6px; padding-bottom: 4px; border-bottom: 1px solid var(--g2); }
.jd-full h2:first-child { margin-top: 4px; }
.jd-full h3 { font-size: .86rem; margin: 12px 0 4px; color: var(--dk); }
.jd-full p, .jd-full li { font-size: .83rem; }
.rbox h3 { font-size: .86rem; margin: 10px 0 4px; }
.rbox blockquote { border-left: 3px solid var(--y); margin: 6px 0; padding: 4px 12px; background: #FFFBEB; border-radius: 0 6px 6px 0; font-size: .83rem; }
.opt-result h3 { font-size: .86rem; font-weight: 700; margin: 10px 0 4px; }
.opt-result blockquote { border-left: 3px solid var(--y); margin: 6px 0; padding: 4px 12px; background: #FFFBEB; border-radius: 0 6px 6px 0; font-size: .83rem; }
@keyframes jdIn { from { opacity: 0; transform: translateY(-4px); } to { opacity: 1; transform: translateY(0); } }
.job-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; margin-bottom: 10px; }
.job-right { display: flex; flex-direction: column; align-items: flex-end; gap: 6px; }
.co { font-size: .78rem; color: var(--g5); }
.ti { font-weight: 700; }
.score { font-size: 1.3rem; font-weight: 900; text-align: right; }
.score span { display: block; font-size: .62rem; font-weight: 600; color: var(--g5); text-transform: uppercase; }
.tags { display: flex; flex-wrap: wrap; gap: 5px; }
.tags span { background: #F8FAFC; border-radius: 5px; padding: 3px 9px; font-size: .76rem; }

/* Source tag */
.src-tag { font-size: .65rem; font-weight: 700; padding: 2px 8px; border-radius: 10px; text-decoration: none; white-space: nowrap; }
.src-preset { background: #F1F5F9; color: #64748B; }
.src-crawled { background: #EFF6FF; color: var(--blue); }
.src-user_posted { background: #ECFDF5; color: var(--green); }
.src-link { cursor: pointer; transition: opacity .15s; }
.src-link:hover { opacity: .72; }

/* Report box */
.rbox { background: #fff; border: 1px solid var(--g2); border-radius: 14px; padding: 24px; line-height: 1.8; }
.rbox h2 { font-size: .95rem; margin: 20px 0 8px; padding-bottom: 6px; border-bottom: 2px solid #FFFBEB; }
.rbox h2:first-child { margin-top: 0; }
.rbox ul { padding-left: 22px; }
.tbl-wrap { overflow-x: auto; margin: 10px 0; }
.md-tbl { width: 100%; border-collapse: collapse; font-size: .85rem; }
.md-tbl th, .md-tbl td { border: 1px solid var(--g2); padding: 8px 12px; text-align: left; vertical-align: top; line-height: 1.6; }
.md-tbl th { background: #F8FAFC; font-weight: 700; white-space: nowrap; }
.md-tbl tr:nth-child(even) td { background: #FAFBFC; }

/* Recruiter form */
.rec-title { font-size: 1.35rem; font-weight: 800; margin-bottom: 24px; }
.form { display: flex; flex-direction: column; gap: 16px; }
.row2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
@media (max-width: 560px) { .row2 { grid-template-columns: 1fr; } }
.field { display: flex; flex-direction: column; gap: 6px; }
.field label { font-size: .82rem; font-weight: 600; color: var(--g5); }
.req { color: #EF4444; }
.inp { border: 1px solid var(--g2); border-radius: 8px; padding: 10px 12px; font-size: .92rem; outline: none; transition: border-color .15s; }
.inp:focus { border-color: var(--y); }
.ta-wrap { position: relative; }
.ta { width: 100%; border: 1px solid var(--g2); border-radius: 8px; padding: 10px 12px; font-size: .92rem; resize: vertical; outline: none; font-family: inherit; transition: border-color .15s; }
.ta:focus { border-color: var(--y); }
.ai-btn { position: absolute; bottom: 10px; right: 10px; background: var(--dk); color: #fff; border: none; border-radius: 6px; padding: 6px 12px; font-size: .75rem; font-weight: 700; cursor: pointer; transition: opacity .15s; }
.ai-btn:hover:not([disabled]) { opacity: .8; }
.ai-btn[disabled] { opacity: .5; cursor: not-allowed; }

/* Profile panel */
.overlay { position: fixed; inset: 0; background: rgba(15,23,42,.35); z-index: 500; display: flex; justify-content: flex-end; }
.panel { background: #fff; width: min(340px, 92vw); height: 100%; padding: 28px 24px; display: flex; flex-direction: column; gap: 14px; overflow-y: auto; }
.panel-hdr { display: flex; align-items: center; justify-content: space-between; }
.panel-title { font-weight: 800; font-size: 1.05rem; }
.close { background: none; border: none; font-size: 1.1rem; cursor: pointer; color: var(--g5); }
.avatar { font-size: 2.5rem; text-align: center; margin-top: 8px; }
.uname { font-weight: 700; text-align: center; font-size: 1.05rem; }
.usub { text-align: center; color: var(--g5); font-size: .82rem; }
.divider { border-top: 1px solid var(--g2); }
.prow { display: flex; align-items: center; justify-content: space-between; font-size: .88rem; }
.sel { border: 1px solid var(--g2); border-radius: 6px; padding: 5px 8px; font-size: .85rem; }
.about-title { font-weight: 700; font-size: .88rem; }
.about-desc { color: var(--g5); font-size: .82rem; line-height: 1.6; }
.ver { font-size: .75rem; color: #CBD5E1; text-align: center; margin-top: auto; }

/* Mode toggle */
.toggle-row { display: flex; align-items: center; justify-content: center; gap: 10px; padding: 4px 0; }
.tog-lbl { font-size: .82rem; color: var(--g5); transition: color .2s; }
.tog-lbl.tog-active { color: var(--dk); font-weight: 700; }
.tog { width: 42px; height: 24px; border-radius: 12px; border: none; background: var(--g2); cursor: pointer; position: relative; transition: background .2s; padding: 0; }
.tog.tog-on { background: var(--dk); }
.tog-thumb { position: absolute; top: 3px; left: 3px; width: 18px; height: 18px; border-radius: 50%; background: #fff; transition: transform .2s; display: block; }
.tog.tog-on .tog-thumb { transform: translateX(18px); }

/* Slide transition for panel */
.slide-enter-active, .slide-leave-active { transition: opacity .2s; }
.slide-enter-active .panel, .slide-leave-active .panel { transition: transform .25s cubic-bezier(.4,0,.2,1); }
.slide-enter-from .panel, .slide-leave-to .panel { transform: translateX(100%); }
.slide-enter-from, .slide-leave-to { opacity: 0; }

.footer { text-align: center; color: #94A3B8; font-size: .78rem; margin-top: 48px; }

/* My posted jobs in profile panel */
.my-job-row { padding: 10px 0; border-bottom: 1px solid var(--g2); }
.my-job-row:last-child { border-bottom: none; }
.my-job-info { display: flex; align-items: center; gap: 8px; margin-bottom: 3px; }
.my-job-title { font-size: .84rem; font-weight: 600; flex: 1; }
.my-job-status { font-size: .68rem; font-weight: 700; padding: 2px 7px; border-radius: 10px; white-space: nowrap; }
.status-active { background: #ECFDF5; color: var(--green); }
.status-closed { background: #F1F5F9; color: var(--g5); }
.my-job-meta { font-size: .75rem; color: var(--g5); margin-bottom: 6px; }
.my-job-actions { display: flex; gap: 6px; }
.btn-sm { border: none; border-radius: 6px; padding: 4px 10px; font-size: .75rem; font-weight: 600; cursor: pointer; }
.btn-close { background: #FEF2F2; color: #DC2626; }
.btn-close:hover { background: #FEE2E2; }
.btn-reopen { background: #F0FDF4; color: #16A34A; }
.btn-reopen:hover { background: #DCFCE7; }
</style>
