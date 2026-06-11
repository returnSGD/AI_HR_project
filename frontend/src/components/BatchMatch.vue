<template>
  <div class="bm" ref="root">
  <div class="bm-scroll">

    <!-- Nav -->
    <nav class="bm-nav">
      <button class="back-btn" @click="handleClose">
        <span class="back-ico">←</span>
        {{ locale === 'zh' ? '返回' : 'Back' }}
      </button>
      <div class="nav-brand">
        <span class="brand-ico">📦</span>
        <span class="brand-word">{{ locale === 'zh' ? '批量筛选' : 'Batch Screening' }}</span>
      </div>
    </nav>

    <div class="bm-body">

      <!-- Header -->
      <header class="bm-hero ai-in" style="--d:0s">
        <div class="hero-tag">
          <span class="tag-dot"></span>
          {{ locale === 'zh' ? 'HR 批量筛选 · AI 排名' : 'HR Batch Screening · AI Ranking' }}
        </div>
        <h1 class="bm-h1">
          <span class="h1-plain">{{ locale === 'zh' ? '批量上传简历' : 'Batch Upload Resumes' }}</span>
          <br>
          <span class="h1-grad">{{ locale === 'zh' ? 'AI 智能排名' : 'AI Smart Ranking' }}</span>
        </h1>
        <p class="bm-sub">
          {{ locale === 'zh'
            ? '一次性上传多份简历，设定岗位要求与招聘人数，AI 自动筛选、评分、横向对比，输出候选人排名'
            : 'Upload multiple resumes at once, set job requirements and headcount, AI auto-screens, scores, and ranks candidates' }}
        </p>
      </header>

      <!-- Error -->
      <transition name="err-fade">
        <div v-if="err" class="err-box">⚠ {{ err }}</div>
      </transition>

      <!-- ═══════════ STEP 1: Upload ═══════════ -->
      <template v-if="step === 1">
        <div class="panel ai-in" style="--d:.14s">
          <div class="panel-hd">
            <div class="panel-ico">📁</div>
            <div>
              <div class="panel-title">{{ locale === 'zh' ? '上传简历' : 'Upload Resumes' }}</div>
              <div class="panel-hint">{{ locale === 'zh' ? '支持 PDF / Word / 图片 / TXT，单文件 ≤10MB，最多 100 份' : 'PDF / Word / Image / TXT, ≤10MB each, max 100 files' }}</div>
            </div>
          </div>

          <label class="drop-zone" :class="{'has-files': files.length}">
            <input type="file" multiple
              accept=".pdf,.doc,.docx,.jpg,.jpeg,.png,.txt,.md,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,image/*"
              @change="pickFiles" hidden />
            <template v-if="!files.length">
              <span class="dz-icon">☁</span>
              <span class="dz-main">{{ locale === 'zh' ? '点击或拖拽上传多份简历' : 'Click or drag to upload resumes' }}</span>
              <span class="dz-sub">PDF · Word · 图片 · TXT · MD（支持多选）</span>
            </template>
            <template v-else>
              <span class="dz-icon has">✓</span>
              <span class="dz-main">{{ locale === 'zh' ? `已选择 ${files.length} 份简历` : `${files.length} resumes selected` }}</span>
              <span class="dz-sub" style="cursor:pointer" @click.prevent="files=[]; err=''">{{ locale === 'zh' ? '点击清除重新选择' : 'Click to clear & re-select' }}</span>
            </template>
          </label>

          <!-- File list preview -->
          <div v-if="files.length" class="file-list">
            <div v-for="(f, i) in files.slice(0, 8)" :key="i" class="file-item">
              <span class="fi-name">{{ f.name }}</span>
              <span class="fi-size">{{ formatSize(f.size) }}</span>
            </div>
            <div v-if="files.length > 8" class="file-more">
              {{ locale === 'zh' ? `...还有 ${files.length - 8} 份` : `...and ${files.length - 8} more` }}
            </div>
          </div>
        </div>

        <div class="center-btn ai-in" style="--d:.28s">
          <button class="cta-btn" :disabled="!files.length" @click="step = 2">
            <span>{{ locale === 'zh' ? '下一步：填写岗位要求 →' : 'Next: Job Requirements →' }}</span>
            <span class="btn-shine"></span>
          </button>
        </div>
      </template>

      <!-- ═══════════ STEP 2: Requirements ═══════════ -->
      <template v-if="step === 2">
        <div class="panel ai-in" style="--d:.08s">
          <div class="panel-hd">
            <div class="panel-ico">📋</div>
            <div>
              <div class="panel-title">{{ locale === 'zh' ? '岗位要求' : 'Job Requirements' }}</div>
              <div class="panel-hint">{{ locale === 'zh' ? '填写越详细，AI 排名越精准' : 'More details = more accurate AI ranking' }}</div>
            </div>
          </div>

          <div class="form-grid">
            <div class="field">
              <label>{{ locale === 'zh' ? '岗位名称' : 'Job Title' }} <span class="req">*</span></label>
              <input class="inp" v-model="req.jobTitle" :placeholder="locale === 'zh' ? '如：算法工程师（实习）' : 'e.g. ML Engineer (Intern)'" />
            </div>
            <div class="field">
              <label>{{ locale === 'zh' ? '招聘人数' : 'Headcount' }} <span class="req">*</span></label>
              <input class="inp inp-sm" type="number" min="1" max="50" v-model.number="req.headcount" />
            </div>
          </div>

          <div class="field" style="margin-top:14px">
            <label>{{ locale === 'zh' ? '职位描述 (JD)' : 'Job Description' }} <span class="req">*</span></label>
            <div class="ta-wrap" :class="{focused: jdFocus}">
              <textarea class="ta"
                v-model="req.jdText"
                :placeholder="locale === 'zh' ? '粘贴完整的职位描述，包括岗位职责、任职要求、技术栈等…' : 'Paste full JD including responsibilities, requirements, tech stack…'"
                @focus="jdFocus=true" @blur="jdFocus=false"
              />
            </div>
            <span :class="['char-cnt', {warn: req.jdText.length > 2800}]">{{ req.jdText.length }} / 3000</span>
          </div>

          <div class="form-grid" style="margin-top:8px">
            <div class="field">
              <label>{{ locale === 'zh' ? '必备技能（硬性过滤）' : 'Required Skills (hard filter)' }}</label>
              <input class="inp" v-model="req.mustSkills" :placeholder="locale === 'zh' ? 'Python, PyTorch, SQL （逗号分隔，简历中至少出现一项）' : 'Python, PyTorch, SQL (comma separated)'" />
            </div>
            <div class="field">
              <label>{{ locale === 'zh' ? '加分技能' : 'Nice-to-Have Skills' }}</label>
              <input class="inp" v-model="req.plusSkills" :placeholder="locale === 'zh' ? 'CUDA, Docker, Kubernetes （逗号分隔）' : 'CUDA, Docker, Kubernetes (comma separated)'" />
            </div>
          </div>

          <div class="form-grid" style="margin-top:8px">
            <div class="field">
              <label>{{ locale === 'zh' ? '最低学历要求' : 'Minimum Education' }}</label>
              <select class="inp sel-inp" v-model.number="req.eduTier">
                <option :value="0">{{ locale === 'zh' ? '不限' : 'Any' }}</option>
                <option :value="1">{{ locale === 'zh' ? 'C9 / QS Top-50' : 'C9 / QS Top-50' }}</option>
                <option :value="2">{{ locale === 'zh' ? '985 / 211 / 双一流' : '985 / 211 / Double First-Class' }}</option>
                <option :value="3">{{ locale === 'zh' ? '本科及以上' : 'Bachelor or above' }}</option>
                <option :value="4">{{ locale === 'zh' ? '专科及以上' : 'Associate or above' }}</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Review card -->
        <div class="review-card ai-in" style="--d:.22s">
          <div class="review-hd">{{ locale === 'zh' ? '📋 确认信息' : '📋 Confirmation' }}</div>
          <div class="review-row"><span class="rv-lbl">{{ locale === 'zh' ? '简历' : 'Resumes' }}</span> <span class="rv-val">{{ files.length }} {{ locale === 'zh' ? '份' : 'files' }}</span></div>
          <div class="review-row"><span class="rv-lbl">{{ locale === 'zh' ? '岗位' : 'Role' }}</span> <span class="rv-val">{{ req.jobTitle || '—' }}</span></div>
          <div class="review-row"><span class="rv-lbl">{{ locale === 'zh' ? '招聘人数' : 'Headcount' }}</span> <span class="rv-val">{{ req.headcount }} {{ locale === 'zh' ? '人' : '' }}</span></div>
          <div class="review-row"><span class="rv-lbl">{{ locale === 'zh' ? 'JD 字数' : 'JD length' }}</span> <span class="rv-val">{{ req.jdText.length }} {{ locale === 'zh' ? '字' : 'chars' }}</span></div>
          <div class="review-row"><span class="rv-lbl">{{ locale === 'zh' ? '必备技能' : 'Required skills' }}</span> <span class="rv-val">{{ req.mustSkills || (locale === 'zh' ? '不限' : 'Any') }}</span></div>
          <div class="review-row"><span class="rv-lbl">{{ locale === 'zh' ? '学历要求' : 'Education' }}</span> <span class="rv-val">{{ eduLabel(req.eduTier) }}</span></div>
          <p class="review-note">
            {{ locale === 'zh' ? '预计耗时约 30~60 秒，取决于简历数量。' : 'Estimated 30–60s depending on resume count.' }}
          </p>
        </div>

        <div class="center-btn ai-in" style="--d:.35s">
          <button class="cta-btn" :disabled="!canStart || loading" @click="run">
            <span v-if="!loading">{{ locale === 'zh' ? '🚀 开始智能排名' : '🚀 Start AI Ranking' }}</span>
            <span v-else>
              <span class="spin-ring"></span>
              {{ statusText }}
            </span>
            <span class="btn-shine"></span>
          </button>
          <button class="ghost-btn" @click="step = 1" :disabled="loading">
            {{ locale === 'zh' ? '← 返回修改简历' : '← Back to resumes' }}
          </button>
        </div>
      </template>

      <!-- ═══════════ STEP 3: Results ═══════════ -->
      <template v-if="step === 3">

        <!-- Loading state -->
        <div v-if="loading" class="phase-loading ai-in" style="--d:0s">
          <div class="phase-ring-wrap">
            <div class="phase-ring"></div>
          </div>
          <div class="phase-text">{{ statusText }}</div>
          <p class="phase-hint">{{ locale === 'zh' ? 'AI 正在逐一深度评估简历，请稍候…' : 'AI is evaluating each resume. Please wait…' }}</p>
        </div>

        <!-- Results area: shown only after loading -->
        <template v-if="!loading">

        <!-- Report header -->
        <div v-if="candidates.length" class="report-hdr ai-in" style="--d:0s">
          <div class="rpt-tag"><span class="rpt-dot"></span>{{ locale === 'zh' ? 'AI 批量筛选完成' : 'AI Screening Complete' }}</div>
          <h2 class="rpt-title">{{ locale === 'zh' ? '候选人排名报告' : 'Candidate Ranking Report' }}</h2>
        </div>

        <!-- Empty state -->
        <div v-if="!candidates.length && !summary" class="empty-state ai-in" style="--d:0s">
          <div class="es-icon">🔍</div>
          <div class="es-title">{{ locale === 'zh' ? '未找到候选人数据' : 'No candidate data' }}</div>
          <div class="es-desc">{{ locale === 'zh' ? '请检查简历文件格式，或降低筛选条件后重试' : 'Check file formats or relax the filter criteria' }}</div>
        </div>

        <!-- Summary card -->
        <div v-if="summary" class="summary-card ai-in" style="--d:0s">
          <div class="sum-grid">
            <div class="sum-item">
              <span class="sum-num">{{ summary.total_uploaded }}</span>
              <span class="sum-lbl">{{ locale === 'zh' ? '上传简历' : 'Uploaded' }}</span>
            </div>
            <div class="sum-sep"></div>
            <div class="sum-item">
              <span class="sum-num green">{{ summary.passed_screening }}</span>
              <span class="sum-lbl">{{ locale === 'zh' ? '进入评估' : 'Evaluated' }}</span>
            </div>
            <div class="sum-sep"></div>
            <div class="sum-item">
              <span class="sum-num gold">{{ summary.headcount }}</span>
              <span class="sum-lbl">{{ locale === 'zh' ? '推荐面试' : 'Recommended' }}</span>
            </div>
            <div class="sum-sep"></div>
            <div class="sum-item">
              <span class="sum-num">{{ summary.avg_score }}</span>
              <span class="sum-lbl">{{ locale === 'zh' ? '平均分' : 'Avg Score' }}</span>
            </div>
          </div>
          <div v-if="summary.overall_assessment" class="sum-assess">
            <span class="assess-dot">✦</span> {{ summary.overall_assessment }}
          </div>
        </div>

        <!-- Distribution bar -->
        <div v-if="summary && summary.score_distribution" class="dist-bar ai-in" style="--d:.08s">
          <div class="dist-seg dist-s1" :style="{flex: summary.score_distribution['90+'] || 0.1}">
            <span v-if="summary.score_distribution['90+']">90+ ({{ summary.score_distribution['90+'] }})</span>
          </div>
          <div class="dist-seg dist-s2" :style="{flex: summary.score_distribution['80-89'] || 0.1}">
            <span v-if="summary.score_distribution['80-89']">80-89 ({{ summary.score_distribution['80-89'] }})</span>
          </div>
          <div class="dist-seg dist-s3" :style="{flex: summary.score_distribution['70-79'] || 0.1}">
            <span v-if="summary.score_distribution['70-79']">70-79 ({{ summary.score_distribution['70-79'] }})</span>
          </div>
          <div class="dist-seg dist-s4" :style="{flex: summary.score_distribution['60-69'] || 0.1}">
            <span v-if="summary.score_distribution['60-69']">60-69 ({{ summary.score_distribution['60-69'] }})</span>
          </div>
          <div class="dist-seg dist-s5" :style="{flex: summary.score_distribution['<60'] || 0.1}">
            <span v-if="summary.score_distribution['<60']">&lt;60 ({{ summary.score_distribution['<60'] }})</span>
          </div>
        </div>

        <!-- Cutoff analysis -->
        <div v-if="summary && summary.cutoff_analysis" class="cutoff-card ai-in" style="--d:.12s">
          <span class="cutoff-icon">✂</span>
          <span>{{ summary.cutoff_analysis }}</span>
        </div>

        <!-- Tier: Strong Recommend -->
        <template v-for="tier in ['strong_recommend', 'consider', 'not_recommend', 'rejected']" :key="tier">
          <div v-if="tierCandidates(tier).length" class="tier-section ai-in" :style="`--d:${['strong_recommend','consider','not_recommend','rejected'].indexOf(tier) * .12 + .16}s`">
            <div :class="['tier-header', `tier-${tier}`]">
              <span class="tier-ico">{{ tierIcons[tier] }}</span>
              <span class="tier-title">{{ tierLabels[tier] }} ({{ tierCandidates(tier).length }})</span>
              <span v-if="tier === 'strong_recommend'" class="tier-cta">{{ locale === 'zh' ? '建议立即安排面试' : 'Recommend immediate interview' }}</span>
            </div>

            <div
              v-for="c in tierCandidates(tier)" :key="c.resume_id"
              :class="['candidate-card', expandedId === c.resume_id && 'expanded']"
              @click="expandedId = expandedId === c.resume_id ? null : c.resume_id"
            >
              <div class="cc-top">
                <div class="cc-rank">#{{ c.rank < 999 ? c.rank : '—' }}</div>
                <div class="cc-info">
                  <div class="cc-name">{{ c.name || c.raw_filename }}</div>
                  <div class="cc-file">{{ c.raw_filename }}</div>
                  <div v-if="c.rank_reason" class="cc-reason">{{ c.rank_reason }}</div>
                </div>
                <div class="cc-score-wrap">
                  <div class="cc-score" :class="scoreClass(c.overall_score)">{{ c.overall_score }}<span class="cc-pct">%</span></div>
                  <div class="cc-badge" :class="`bdg-${tier}`">{{ tierBadges[tier] }}</div>
                  <div v-if="c._fallback" class="cc-fallback-badge">⚡ {{ locale === 'zh' ? '规则引擎' : 'Rule-based' }}</div>
                </div>
              </div>

              <!-- Score breakdown bars -->
              <div v-if="c.score_breakdown && Object.keys(c.score_breakdown).length" class="cc-bars">
                <div v-for="(val, key) in c.score_breakdown" :key="key" class="cc-bar-row">
                  <span class="cc-bar-lbl">{{ scoreLabels[key] || key }}</span>
                  <div class="cc-bar-track">
                    <div class="cc-bar-fill" :class="barColor(val)" :style="{width: val + '%'}"></div>
                  </div>
                  <span class="cc-bar-val">{{ val }}</span>
                </div>
              </div>

              <!-- Highlights & Gaps -->
              <div class="cc-highlights" v-if="c.match_highlights?.length">
                <span class="cc-hl-label">✅</span>
                <span v-for="h in c.match_highlights" :key="h" class="cc-chip chip-good">{{ h }}</span>
              </div>
              <div class="cc-gaps" v-if="c.key_gaps?.length">
                <span class="cc-hl-label">❌</span>
                <span v-for="g in c.key_gaps" :key="g" class="cc-chip chip-bad">{{ g }}</span>
              </div>

              <!-- LLM Comment -->
              <div v-if="c.llm_comment" class="cc-comment">💬 {{ c.llm_comment }}</div>

              <div class="cc-expand-hint">{{ expandedId === c.resume_id ? '▲' : '▼' }}</div>
            </div>
          </div>
        </template>

        <!-- Actions -->
        <div v-if="candidates.length" class="center-btn" style="margin-top:32px">
          <button class="cta-btn" @click="copyReport">
            {{ locale === 'zh' ? '📋 复制排名报告' : '📋 Copy Ranking Report' }}
            <span class="btn-shine"></span>
          </button>
        </div>
        <div class="center-btn" style="margin-top:12px">
          <button class="ghost-btn" @click="reset">
            {{ locale === 'zh' ? '↺ 开始新的筛选' : '↺ Start New Screening' }}
          </button>
        </div>

        </template><!-- /v-if="!loading" -->
      </template><!-- /step 3 -->

    </div>
  </div><!-- /bm-scroll -->
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'

const emit = defineEmits(['close'])
const { locale } = useI18n()

const API_BASE = import.meta.env.DEV ? '' : 'https://offer-catcher-api.onrender.com'

// ── Steps ────────────────────────────────────────────────────
const step = ref(1)

// ── Step 1: Files ────────────────────────────────────────────
const files = ref([])
const root = ref(null)

function pickFiles(e) {
  const selected = Array.from(e.target.files || [])
  files.value = [...files.value, ...selected].slice(0, 100)
  err.value = ''
}

function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

// ── Step 2: Requirements ─────────────────────────────────────
const req = ref({
  jobTitle: '',
  jdText: '',
  mustSkills: '',
  plusSkills: '',
  eduTier: 0,
  headcount: 3,
})
const jdFocus = ref(false)

const canStart = computed(() =>
  files.value.length > 0 &&
  req.value.jobTitle.trim().length > 0 &&
  req.value.jdText.trim().length >= 20
)

function eduLabel(tier) {
  const map = { 0: '不限 / Any', 1: 'C9 / QS Top-50', 2: '985/211/双一流', 3: '本科及以上', 4: '专科及以上' }
  return map[tier] || '不限'
}

// ── Step 3: Results ──────────────────────────────────────────
const loading = ref(false)
const statusText = ref('')
const err = ref('')
const candidates = ref([])
const summary = ref(null)
const expandedId = ref(null)

async function run() {
  if (!canStart.value) return
  err.value = ''
  candidates.value = []
  summary.value = null
  step.value = 3
  loading.value = true
  statusText.value = locale.value === 'zh' ? '正在上传简历…' : 'Uploading resumes…'

  try {
    const fd = new FormData()
    files.value.forEach(f => fd.append('files', f))
    fd.append('job_title', req.value.jobTitle)
    fd.append('jd_text', req.value.jdText.slice(0, 3000))
    fd.append('must_skills', req.value.mustSkills)
    fd.append('plus_skills', req.value.plusSkills)
    fd.append('education_tier', String(req.value.eduTier))
    fd.append('headcount', String(req.value.headcount))

    const resp = await fetch(`${API_BASE}/api/batch-match`, {
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
      const lines = buf.split('\n')
      buf = lines.pop() || ''
      for (const line of lines) {
        if (!line.startsWith('data: ')) continue
        const obj = JSON.parse(line.slice(6))
        if (obj.type === 'progress') {
          statusText.value = obj.text
        } else if (obj.type === 'warning') {
          console.warn('[batch-match]', obj.message)
        } else if (obj.type === 'result') {
          candidates.value = obj.candidates || []
          summary.value = obj.summary || null
          loading.value = false
        } else if (obj.type === 'error') {
          throw new Error(obj.message)
        } else if (obj.type === 'done') {
          loading.value = false
        }
      }
    }
  } catch (e) {
    err.value = e.message
    loading.value = false
    step.value = 2
  }
}

// ── Tier helpers ──────────────────────────────────────────────
const tierIcons = {
  strong_recommend: '🥇',
  consider: '💡',
  not_recommend: '❌',
  rejected: '🚫',
}
const tierLabels = computed(() => ({
  strong_recommend: locale.value === 'zh' ? '强烈推荐 — 建议立即安排面试' : 'Strongly Recommend — Interview Now',
  consider: locale.value === 'zh' ? '可考虑 — 如推荐人选不足可递补' : 'Consider — Backup candidates',
  not_recommend: locale.value === 'zh' ? '暂不推荐' : 'Not Recommended',
  rejected: locale.value === 'zh' ? '已淘汰（初筛未通过）' : 'Rejected (Failed Screening)',
}))
const tierBadges = {
  strong_recommend: '🥇',
  consider: '💡',
  not_recommend: '',
  rejected: '🚫',
}

function tierCandidates(tier) {
  return candidates.value.filter(c => c.tier === tier)
}

const scoreLabels = computed(() => locale.value === 'zh' ? {
  skill_match: '技能匹配',
  education_fit: '学历契合',
  experience_fit: '经验相关',
  project_relevance: '项目关联',
  overall_quality: '整体质量',
} : {
  skill_match: 'Skill Match',
  education_fit: 'Education',
  experience_fit: 'Experience',
  project_relevance: 'Projects',
  overall_quality: 'Quality',
})

function scoreClass(s) {
  if (s >= 85) return 'sc-high'
  if (s >= 70) return 'sc-mid'
  return 'sc-low'
}

function barColor(v) {
  if (v >= 80) return 'bar-high'
  if (v >= 60) return 'bar-mid'
  return 'bar-low'
}

function copyReport() {
  let text = `=== ${locale.value === 'zh' ? '批量筛选报告' : 'Batch Screening Report'} ===\n\n`
  if (summary.value) {
    text += `${locale.value === 'zh' ? '上传' : 'Uploaded'}: ${summary.value.total_uploaded} | ${locale.value === 'zh' ? '通过初筛' : 'Passed'}: ${summary.value.passed_screening} | ${locale.value === 'zh' ? '招聘人数' : 'Headcount'}: ${summary.value.headcount} | ${locale.value === 'zh' ? '平均分' : 'Avg'}: ${summary.value.avg_score}\n`
    if (summary.value.overall_assessment) text += `\n${summary.value.overall_assessment}\n`
    if (summary.value.cutoff_analysis) text += `\n✂ ${summary.value.cutoff_analysis}\n`
    text += '\n'
  }
  for (const t of ['strong_recommend', 'consider', 'not_recommend', 'rejected']) {
    const cs = tierCandidates(t)
    if (!cs.length) continue
    text += `\n--- ${tierLabels.value[t]} ---\n`
    cs.forEach(c => {
      text += `#${c.rank < 999 ? c.rank : '—'} ${c.name || c.raw_filename} — ${c.overall_score}%`
      if (c.llm_comment) text += `\n  💬 ${c.llm_comment}`
      if (c.rank_reason) text += `\n  → ${c.rank_reason}`
      text += '\n'
    })
  }
  navigator.clipboard.writeText(text).then(() => {
    alert(locale.value === 'zh' ? '已复制到剪贴板 ✓' : 'Copied to clipboard ✓')
  }).catch(() => {})
}

function reset() {
  step.value = 1
  files.value = []
  candidates.value = []
  summary.value = null
  err.value = ''
  loading.value = false
  expandedId.value = null
  req.value = { jobTitle: '', jdText: '', mustSkills: '', plusSkills: '', eduTier: 0, headcount: 3 }
}

function handleClose() {
  if (step.value === 3 && candidates.value.length) {
    if (confirm(locale.value === 'zh' ? '确定离开？当前筛选结果将丢失。' : 'Leave? Current results will be lost.')) {
      reset()
      emit('close')
    }
  } else {
    emit('close')
  }
}
</script>

<style scoped>
/* 1. 恢复原状，确保全屏覆盖 */
.bm {
  position: fixed; inset: 0;
  z-index: 150;
  background: #050510;
  color: #e2e8f0;
  font-family: -apple-system, 'SF Pro Text', 'Inter', sans-serif;
  -webkit-font-smoothing: antialiased;
}

/* 2. 彻底移除上一次错误的 display: flex，恢复原生滚动流 */
.bm-scroll {
  width: 100%;
  height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
}

/* 3. 恢复原生导航栏 */
.bm-nav {
  position: sticky; top: 0; z-index: 200;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 28px; height: 56px;
  background: rgba(5,5,16,.92);
  backdrop-filter: saturate(180%) blur(24px);
  -webkit-backdrop-filter: saturate(180%) blur(24px);
  border-bottom: 1px solid rgba(255,255,255,.06);
}
.back-btn {
  display: flex; align-items: center; gap: 7px;
  background: rgba(255,255,255,.06); border: 1px solid rgba(255,255,255,.1);
  color: #94a3b8; border-radius: 980px; padding: 6px 16px;
  font-size: .8rem; font-weight: 600; cursor: pointer;
  transition: all .4s cubic-bezier(0.22,1,0.36,1);
}
.back-btn:hover { background: rgba(255,255,255,.11); color: #f1f5f9; transform: translateX(-2px); }
.back-ico { transition: transform .35s cubic-bezier(0.22,1,0.36,1); }
.back-btn:hover .back-ico { transform: translateX(-3px); }
.nav-brand { display: flex; align-items: center; gap: 8px; }
.brand-ico { font-size: 1rem; }
.brand-word { font-weight: 700; font-size: .9rem; color: #f1f5f9; letter-spacing: -.01em; }

/* 4. 【核心修复】使用相对定位暴力居中主体，无视外部框架干扰 */
.bm-body {
  position: relative;
  left: 50%;
  transform: translateX(-50%); /* 强行拉回中心绝对中轴线 */
  width: 600px;
  max-width: calc(100% - 32px);
  padding: 40px 16px 100px;
  box-sizing: border-box;
  margin: 0; /* 清除原先失效的 margin: auto */
}
@media (max-width: 800px) {
  .bm-body { padding: 28px 16px 80px; }
  .bm-nav { padding: 0 16px; }
  .brand-word { display: none; }
}

/* ── Hero ── */
.bm-hero { text-align: center; margin-bottom: 36px; }
.hero-tag {
  display: inline-flex; align-items: center; gap: 8px;
  font-size: .72rem; font-weight: 700; letter-spacing: .07em; text-transform: uppercase;
  color: #818cf8;
  background: rgba(99,102,241,.1); border: 1px solid rgba(99,102,241,.25);
  padding: 5px 15px; border-radius: 20px; margin-bottom: 20px;
}
.tag-dot { width: 6px; height: 6px; border-radius: 50%; background: #818cf8; animation: dot-pulse 2s ease-in-out infinite; }
@keyframes dot-pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.4;transform:scale(.75)} }
.bm-h1 {
  font-size: clamp(1.8rem, 5vw, 2.6rem);
  font-weight: 800; line-height: 1.12; letter-spacing: -.03em; margin: 0 0 14px;
}
.h1-plain { color: #f1f5f9; }
.h1-grad {
  background: linear-gradient(135deg, #818cf8, #c084fc, #67e8f9);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
  background-size: 200% 200%;
  animation: grad-anim 6s ease-in-out infinite alternate;
}
@keyframes grad-anim { from{background-position:0% 50%} to{background-position:100% 50%} }
.bm-sub { font-size: .88rem; color: #64748b; max-width: 560px; margin: 0 auto; line-height: 1.65; }

.ai-in {
  opacity: 0; transform: translateY(24px);
  animation: fadeUp .85s cubic-bezier(0.22,1,0.36,1) both;
  animation-delay: var(--d, 0s);
}
@keyframes fadeUp { to { opacity:1; transform:translateY(0); } }

/* ── Error ── */
.err-box {
  max-width: 760px; margin: 0 auto 18px;
  background: rgba(254,202,202,.08); border: 1px solid rgba(252,165,165,.25);
  border-radius: 14px; padding: 12px 18px; color: #fca5a5; font-size: .85rem;
}
.err-fade-enter-active, .err-fade-leave-active { transition: opacity .35s, transform .35s cubic-bezier(0.22,1,0.36,1); }
.err-fade-enter-from, .err-fade-leave-to { opacity: 0; transform: translateY(-8px); }

/* ── Panel ── */
.panel {
  width: auto; height: auto; display: block;
  background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.07);
  border-left: 1px solid rgba(255,255,255,.07);
  border-radius: 20px; padding: 26px 24px; margin-bottom: 20px;
  box-shadow: none; gap: normal;
  backdrop-filter: none; -webkit-backdrop-filter: none;
  overflow-y: visible;
}
.panel-hd { display: flex; align-items: flex-start; gap: 12px; margin-bottom: 18px; }
.panel-ico {
  font-size: 1.3rem; width: 42px; height: 42px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
  background: rgba(139,92,246,.15); border: 1px solid rgba(139,92,246,.25);
}
.panel-title { font-size: .9rem; font-weight: 700; color: #f1f5f9; letter-spacing: -.01em; }
.panel-hint { font-size: .72rem; color: #64748b; margin-top: 2px; }

/* ── Drop zone ── */
.drop-zone {
  display: block; border: 1.5px dashed rgba(139,92,246,.3);
  border-radius: 18px; background: rgba(139,92,246,.04);
  padding: 40px 24px; text-align: center;
  cursor: pointer; transition: all .45s cubic-bezier(0.22,1,0.36,1);
}
.drop-zone:hover {
  border-color: rgba(139,92,246,.6); background: rgba(139,92,246,.1);
  transform: scale(1.01) translateY(-2px);
}
.drop-zone.has-files { border-style: solid; border-color: rgba(52,211,153,.4); background: rgba(52,211,153,.06); }
.dz-icon { display: block; font-size: 2.2rem; margin-bottom: 10px; color: #a78bfa; opacity: .7; }
.dz-icon.has { color: #34d399; }
.dz-main { display: block; font-size: .9rem; font-weight: 600; color: #cbd5e1; }
.dz-sub { display: block; font-size: .73rem; color: #475569; margin-top: 6px; }

/* ── File list ── */
.file-list { margin-top: 14px; }
.file-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 8px 12px; border-radius: 8px;
  background: rgba(255,255,255,.03); border: 1px solid rgba(255,255,255,.05);
  margin-bottom: 4px;
}
.fi-name { font-size: .8rem; color: #cbd5e1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex: 1; }
.fi-size { font-size: .7rem; color: #475569; margin-left: 12px; flex-shrink: 0; }
.file-more { font-size: .76rem; color: #64748b; text-align: center; padding: 6px; }

/* ── Form ── */
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
@media (max-width: 640px) { .form-grid { grid-template-columns: 1fr; } }
.field { display: flex; flex-direction: column; gap: 6px; min-width: 0; }
.field label { font-size: .74rem; font-weight: 600; color: #64748b; letter-spacing: .03em; text-transform: uppercase; }
.req { color: #f87171; }
.inp {
  border: 1.5px solid rgba(255,255,255,.1); border-radius: 12px;
  padding: 10px 14px; font-size: .88rem; outline: none;
  background: rgba(255,255,255,.05); color: #e2e8f0; font-family: inherit;
  transition: border-color .35s cubic-bezier(0.22,1,0.36,1), box-shadow .35s cubic-bezier(0.22,1,0.36,1);
}
.inp::placeholder { color: #334155; }
.inp:focus { border-color: #8b5cf6; box-shadow: 0 0 0 3px rgba(139,92,246,.14); }
.inp-sm { max-width: 120px; }
.sel-inp { cursor: pointer; appearance: none; -webkit-appearance: none; }
.sel-inp option { background: #0f0f1e; color: #e2e8f0; }

.ta-wrap {
  border: 1.5px solid rgba(255,255,255,.08);
  border-radius: 14px; overflow: hidden;
  max-height: 220px; transition: border-color .35s, box-shadow .35s;
}
.ta-wrap.focused { border-color: rgba(139,92,246,.5); box-shadow: 0 0 0 3px rgba(139,92,246,.12); }
.ta {
  display: block; width: 100%; height: 180px; max-height: 210px; overflow-y: auto;
  background: rgba(255,255,255,.03); color: #e2e8f0; border: none; outline: none; resize: none;
  padding: 14px 16px; font-size: .85rem; line-height: 1.7; font-family: inherit;
}
.ta::placeholder { color: #334155; }
.char-cnt { display: block; text-align: right; font-size: .68rem; color: #475569; margin-top: 4px; }
.char-cnt.warn { color: #f87171; }

/* ── Review card ── */
.review-card {
  background: rgba(139,92,246,.06); border: 1px solid rgba(139,92,246,.2);
  border-radius: 16px; padding: 20px; margin: 16px 0 20px;
}
.review-hd { font-weight: 700; font-size: .85rem; color: #c4b5fd; margin-bottom: 12px; }
.review-row { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,.04); }
.review-row:last-of-type { border-bottom: none; }
.rv-lbl { font-size: .8rem; color: #64748b; }
.rv-val { font-size: .82rem; color: #cbd5e1; font-weight: 600; text-align: right; }
.review-note { font-size: .73rem; color: #475569; margin-top: 10px; text-align: center; }

/* ── Buttons ── */
.center-btn { text-align: center; margin-top: 18px; }
.cta-btn {
  position: relative; overflow: hidden;
  display: inline-block;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border: none; border-radius: 980px;
  padding: 13px 30px;
  font-size: .9rem; font-weight: 700; color: #fff; letter-spacing: -.01em;
  cursor: pointer;
  box-shadow: 0 4px 22px rgba(99,102,241,.38);
  transition: transform .45s cubic-bezier(0.22,1,0.36,1), box-shadow .45s;
  will-change: transform;
}
.cta-btn:disabled { opacity: .45; cursor: not-allowed; transform: none !important; box-shadow: none !important; }
.cta-btn:not(:disabled):hover { transform: scale(1.03) translateY(-2px); box-shadow: 0 8px 32px rgba(99,102,241,.52); }
.cta-btn:not(:disabled):active { transform: scale(.97); transition-duration: .1s; }
.btn-shine {
  position: absolute; inset: 0;
  background: linear-gradient(110deg, transparent 30%, rgba(255,255,255,.2) 50%, transparent 70%);
  transform: translateX(-100%); transition: transform 0s;
}
.cta-btn:not(:disabled):hover .btn-shine { transform: translateX(100%); transition: transform .5s ease; }
.ghost-btn {
  display: block; width: 100%; max-width: 280px; margin: 12px auto 0;
  background: transparent; border: 1px solid rgba(255,255,255,.1);
  border-radius: 12px; padding: 10px;
  font-size: .83rem; font-weight: 600; color: #64748b; cursor: pointer;
  transition: all .4s cubic-bezier(0.22,1,0.36,1);
}
.ghost-btn:hover { border-color: rgba(255,255,255,.22); color: #94a3b8; background: rgba(255,255,255,.04); }
.ghost-btn:disabled { opacity: .4; cursor: not-allowed; }
.spin-ring {
  display: inline-block; width: 14px; height: 14px; vertical-align: middle; margin-right: 8px;
  border: 2px solid rgba(255,255,255,.3); border-top-color: #fff;
  border-radius: 50%; animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Phase loading (Step 3) ── */
.phase-loading {
  text-align: center; padding: 80px 24px 60px;
}
.phase-ring-wrap {
  width: 64px; height: 64px; margin: 0 auto 24px;
}
.phase-ring {
  width: 64px; height: 64px; border-radius: 50%;
  border: 3px solid rgba(99,102,241,.2); border-top-color: #818cf8;
  animation: spin 1s linear infinite;
}
.phase-text {
  font-size: .92rem; font-weight: 600; color: #e2e8f0; margin-bottom: 10px;
  min-height: 1.4em;
}
.phase-hint { font-size: .78rem; color: #475569; line-height: 1.6; }

/* ── Report header (Step 3) ── */
.report-hdr { text-align: center; margin-bottom: 28px; }
.rpt-tag {
  display: inline-flex; align-items: center; gap: 7px;
  font-size: .7rem; font-weight: 700; letter-spacing: .06em; text-transform: uppercase;
  color: #34d399; background: rgba(52,211,153,.1); border: 1px solid rgba(52,211,153,.25);
  padding: 4px 14px; border-radius: 20px; margin-bottom: 12px;
}
.rpt-dot {
  width: 6px; height: 6px; border-radius: 50%; background: #34d399;
  animation: dot-pulse 2s ease-in-out infinite;
}
.rpt-title {
  font-size: clamp(1.4rem, 4vw, 2rem); font-weight: 800;
  letter-spacing: -.03em; color: #f1f5f9; margin: 0;
}

/* ── Empty state ── */
.empty-state {
  text-align: center; padding: 60px 24px;
}
.es-icon { font-size: 2.4rem; margin-bottom: 16px; }
.es-title { font-size: 1rem; font-weight: 700; color: #f1f5f9; margin-bottom: 8px; }
.es-desc { font-size: .83rem; color: #475569; line-height: 1.6; max-width: 360px; margin: 0 auto; }

/* ── Summary card ── */
.summary-card {
  background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.08);
  border-radius: 18px; padding: 22px; margin-bottom: 16px;
}
.sum-grid { display: flex; align-items: center; justify-content: space-around; gap: 8px; }
.sum-item { text-align: center; }
.sum-num { font-size: 1.8rem; font-weight: 800; color: #f1f5f9; letter-spacing: -.03em; }
.sum-num.green { color: #34d399; }
.sum-num.gold { color: #f59e0b; }
.sum-lbl { display: block; font-size: .68rem; color: #64748b; margin-top: 4px; text-transform: uppercase; letter-spacing: .04em; }
.sum-sep { width: 1px; height: 36px; background: rgba(255,255,255,.08); }
.sum-assess {
  margin-top: 14px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,.06);
  font-size: .82rem; color: #94a3b8; line-height: 1.65;
  display: flex; align-items: flex-start; gap: 8px;
}
.assess-dot { color: #a78bfa; flex-shrink: 0; margin-top: 1px; }

/* ── Distribution bar ── */
.dist-bar { display: flex; border-radius: 8px; overflow: hidden; height: 28px; margin-bottom: 14px; }
.dist-seg { display: flex; align-items: center; justify-content: center; font-size: .65rem; font-weight: 700; color: #fff; min-width: 20px; }
.dist-s1 { background: #34d399; }
.dist-s2 { background: #60a5fa; }
.dist-s3 { background: #f59e0b; }
.dist-s4 { background: #f87171; }
.dist-s5 { background: #374151; }

/* ── Cutoff card ── */
.cutoff-card {
  display: flex; align-items: flex-start; gap: 10px;
  background: rgba(245,158,11,.08); border: 1px solid rgba(245,158,11,.2);
  border-radius: 12px; padding: 13px 16px; margin-bottom: 18px;
  font-size: .82rem; color: #fbbf24; line-height: 1.6;
}
.cutoff-icon { flex-shrink: 0; margin-top: 1px; font-size: .9rem; }

/* ── Tier sections ── */
.tier-section { margin-bottom: 22px; }
.tier-header {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 16px; border-radius: 12px; margin-bottom: 8px;
}
.tier-strong_recommend { background: rgba(52,211,153,.1); border: 1px solid rgba(52,211,153,.25); }
.tier-consider { background: rgba(96,165,250,.08); border: 1px solid rgba(96,165,250,.18); }
.tier-not_recommend { background: rgba(255,255,255,.03); border: 1px solid rgba(255,255,255,.06); }
.tier-rejected { background: rgba(248,113,113,.05); border: 1px solid rgba(248,113,113,.15); }
.tier-ico { font-size: 1.1rem; flex-shrink: 0; }
.tier-title { font-weight: 700; font-size: .85rem; color: #f1f5f9; flex: 1; letter-spacing: -.01em; }
.tier-cta { font-size: .72rem; font-weight: 600; color: #34d399; white-space: nowrap; }

/* ── Candidate card ── */
.candidate-card {
  background: rgba(255,255,255,.03); border: 1px solid rgba(255,255,255,.06);
  border-radius: 14px; padding: 16px 18px; margin-bottom: 6px;
  cursor: pointer; position: relative;
  transition: transform .5s cubic-bezier(0.22,1,0.36,1), box-shadow .5s, border-color .35s;
}
.candidate-card:hover {
  border-color: rgba(139,92,246,.3);
  box-shadow: 0 8px 28px rgba(99,102,241,.15);
  transform: translateY(-2px);
}
.candidate-card.expanded { border-color: rgba(139,92,246,.4); background: rgba(139,92,246,.05); }
.cc-top { display: flex; align-items: flex-start; gap: 14px; }
.cc-rank {
  font-size: 1.3rem; font-weight: 800; color: #f1f5f9; letter-spacing: -.02em;
  min-width: 42px; flex-shrink: 0;
}
.cc-info { flex: 1; min-width: 0; }
.cc-name { font-size: .9rem; font-weight: 700; color: #f1f5f9; letter-spacing: -.01em; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.cc-file { font-size: .72rem; color: #475569; margin-top: 2px; }
.cc-reason { font-size: .76rem; color: #a78bfa; margin-top: 4px; font-style: italic; line-height: 1.5; }
.cc-score-wrap { text-align: right; flex-shrink: 0; }
.cc-score { font-size: 1.5rem; font-weight: 800; letter-spacing: -.04em; }
.cc-score.sc-high { color: #34d399; }
.cc-score.sc-mid { color: #f59e0b; }
.cc-score.sc-low { color: #f87171; }
.cc-pct { font-size: .75rem; }
.cc-badge { font-size: .85rem; margin-top: 2px; }
.cc-fallback-badge { font-size: .62rem; font-weight: 700; color: #f59e0b; margin-top: 2px; }

/* ── Score bars ── */
.cc-bars { margin-top: 14px; display: flex; flex-direction: column; gap: 6px; }
.cc-bar-row { display: flex; align-items: center; gap: 8px; }
.cc-bar-lbl { font-size: .7rem; color: #64748b; width: 70px; flex-shrink: 0; text-align: right; }
.cc-bar-track { flex: 1; height: 6px; background: rgba(255,255,255,.06); border-radius: 3px; overflow: hidden; }
.cc-bar-fill { height: 100%; border-radius: 3px; transition: width .5s cubic-bezier(0.22,1,0.36,1); }
.bar-high { background: #34d399; }
.bar-mid { background: #f59e0b; }
.bar-low { background: #f87171; }
.cc-bar-val { font-size: .7rem; color: #94a3b8; width: 24px; text-align: left; font-weight: 600; }

/* ── Chips ── */
.cc-highlights, .cc-gaps { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 10px; align-items: center; }
.cc-hl-label { font-size: .68rem; margin-right: 2px; }
.cc-chip {
  font-size: .7rem; padding: 3px 10px; border-radius: 12px; font-weight: 500;
  transition: transform .3s cubic-bezier(.34,1.56,.64,1);
  cursor: default;
}
.cc-chip:hover { transform: scale(1.08); }
.chip-good { background: rgba(52,211,153,.1); color: #34d399; border: 1px solid rgba(52,211,153,.2); }
.chip-bad { background: rgba(248,113,113,.1); color: #f87171; border: 1px solid rgba(248,113,113,.2); }

.cc-comment {
  margin-top: 12px; font-size: .8rem; color: #94a3b8; line-height: 1.65;
  padding: 10px 14px; background: rgba(255,255,255,.03); border-radius: 10px;
}

.cc-expand-hint {
  position: absolute; bottom: 10px; right: 14px; font-size: .6rem; color: rgba(255,255,255,.15);
  transition: color .35s, transform .4s cubic-bezier(.34,1.56,.64,1);
}
.candidate-card:hover .cc-expand-hint { color: rgba(255,255,255,.4); transform: scale(1.25); }

/* ── Responsive ── */
@media (max-width: 600px) {
  .bm-body { padding: 32px 14px 80px; }
  .sum-grid { flex-wrap: wrap; gap: 16px; }
  .sum-sep { display: none; }
}
</style>
