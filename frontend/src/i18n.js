import { createI18n } from 'vue-i18n'

const messages = {
  zh: {
    badge: '测试版',
    nav: { new: '↺ 新的分析', profile: '个人主页' },
    hero: {
      l1: '让 AI 帮你找到', accent: '梦想工作', l2: '',
      sub: '上传简历 · 智能匹配顶级职位 · 获取由 Claude AI 驱动的个性化优化报告'
    },
    upload: { drag: '拖拽或点击上传简历文件', pick: '支持 PDF / Word / Excel / 图片 / TXT / MD' },
    btn: { run: '✨ 分析我的简历', new: '↺ 新的分析', again: '↺ 分析其他简历' },
    status: { read: '正在读取您的简历…', match: '正在与职位数据库匹配…' },
    job: { match: '匹配度', apply: '查看原帖', posted: '发布于', loadingJd: '正在生成职位详情…', matchedSkills: '已具备', missingSkills: '欠缺', optimizeBtn: '✨ 针对此岗位优化我的简历', optimizing: '分析中…', matchTip: '关键词覆盖率：衡量岗位方向与你背景的相关性，帮助你找到合适的方向，并非录取概率', hrBtn: '🎭 模拟 HR 阅读我的简历', hrViewing: 'HR 正在阅读…' },
    section: { jobs: '📊 找到前 {n} 个匹配职位', report: '🤖 AI 诊断报告', generating: '生成中…', complete: '完成 ✓', liveJobs: '个腾讯实时岗', matchNote: '匹配度 = 关键词覆盖率，反映岗位方向与你背景的相关性，≠ 录取概率；点开岗位可获取具体简历优化建议' },
    error: { pdf: '请选择 PDF 文件。', fileType: '不支持的文件格式，请上传 PDF、Word、Excel、图片、TXT 或 MD 文件。', api: '发生意外错误，请稍后重试。' },
    source: { preset: '📦 预设', crawled: '🌐 真实抓取', user_posted: '🏢 企业直招' },
    filter: { province: '省/地区', city: '城市', allCity: '全省/全区', type: '岗位类型', all: '不限', intern: '实习', campus: '校招', fulltime: '全职' },
    mode: { seeker: '求职者', recruiter: '招聘者' },
    recruiter: {
      title: '发布岗位',
      company: '企业名称', companyPh: '如：腾讯、字节跳动',
      jobTitle: '职位名称', jobTitlePh: '如：算法工程师（实习）',
      salary: '薪资', salaryPh: '如：15-30K·14薪',
      location: '工作地点', locationPh: '如：深圳·校招',
      tags: '技能标签', tagsPh: '用英文逗号分隔，如：Python, PyTorch',
      desc: '职位描述', descPh: '用大白话描述岗位需求，或先用 AI 帮你生成…',
      aiBtn: '✨ AI 润色',
      aiLoading: 'AI 生成中…',
      submit: '🚀 发布岗位',
      toast: '岗位发布成功 ✓',
      required: '请填写企业名称和职位名称',
    },
    footer: 'Offer-Catcher · AI 驱动的职位匹配 · 演示应用 · 基于 Claude 构建',
    profile: {
      title: '个人主页', guest: '访客用户', guestSub: '求职者',
      settings: '设置', langLabel: '界面语言', about: '关于应用',
      aboutDesc: 'Offer-Catcher 是一款 AI 驱动的职位智能匹配工具，帮助求职者精准定位最适合的职位，并提供个性化的简历优化建议。',
      version: '版本 1.0.0 Beta', applyNote: '语言设置将在下次分析时生效',
      showPreset: '显示预设职位',
      myJobs: '我发布的岗位', jobActive: '招聘中', jobClosed: '已关闭',
      closeJob: '标记已招到', reopenJob: '重新开放',
      closedToast: '岗位已关闭 ✓', reopenedToast: '岗位已重新开放 ✓',
      jdmatch: 'JD 精准匹配',
      jdmatchDesc: '粘贴任意 JD，分析与你简历的契合度',
      batch: '📦 批量筛选 (HR)',
      batchDesc: '批量上传简历，AI 自动评分排名',
    },
    jdm: {
      title: 'JD 精准匹配',
      sub: '粘贴来自任意招聘平台的职位描述，上传你的简历，AI 深度分析两者的匹配度',
      jdLabel: '职位描述 (JD)',
      jdPh: '将职位描述粘贴到这里…\n\n例如从招聘官网、BOSS 直聘、猎聘等复制完整 JD 内容',
      clear: '清空',
      resumeLabel: '我的简历',
      uploadHint: '📋 点击上传简历文件',
      analyzeBtn: '🔍 分析匹配度',
      analyzing: '分析中…',
      requireBoth: '请先粘贴 JD 并上传简历',
      reset: '↺ 重新分析',
    }
  },
  en: {
    badge: 'Beta',
    nav: { new: '↺ New Analysis', profile: 'Profile' },
    hero: {
      l1: 'Land Your', accent: 'Dream Job', l2: 'With AI-Powered Matching',
      sub: 'Upload your resume · get matched to top-tier roles · receive a personalized optimization report powered by Claude AI.'
    },
    upload: { drag: 'Drop or click to upload your resume', pick: 'PDF / Word / Excel / Image / TXT / MD supported' },
    btn: { run: '✨ Analyze My Resume', new: '↺ New Analysis', again: '↺ Analyze Another Resume' },
    status: { read: 'Reading your resume…', match: 'Matching against job database…' },
    job: { match: 'Match', apply: 'View Job', posted: 'Posted', loadingJd: 'Generating job details…', matchedSkills: 'Have', missingSkills: 'Missing', optimizeBtn: '✨ Optimize My Resume for This Job', optimizing: 'Analyzing…', matchTip: 'Keyword coverage rate — measures directional fit between your background and the role, not your odds of being hired', hrBtn: '🎭 Simulate HR Reading My Resume', hrViewing: 'HR is reading…' },
    section: { jobs: '📊 Top {n} Matches Found', report: '🤖 AI Diagnostic Report', generating: 'Generating…', complete: 'Complete ✓', liveJobs: 'live from Tencent', matchNote: 'Match % = keyword coverage (directional fit), not acceptance probability. Click any card for resume optimization tips.' },
    error: { pdf: 'Please select a PDF file.', fileType: 'Unsupported format. Please upload PDF, Word, Excel, image, TXT, or MD.', api: 'An unexpected error occurred. Please try again.' },
    source: { preset: '📦 Preset', crawled: '🌐 Live', user_posted: '🏢 Direct' },
    filter: { province: 'Province', city: 'City', allCity: 'All Cities', type: 'Job Type', all: 'Any', intern: 'Intern', campus: 'Campus Hire', fulltime: 'Full-time' },
    mode: { seeker: 'Job Seeker', recruiter: 'Recruiter' },
    recruiter: {
      title: 'Post a Job',
      company: 'Company', companyPh: 'e.g. Google, OpenAI',
      jobTitle: 'Job Title', jobTitlePh: 'e.g. ML Engineer (Intern)',
      salary: 'Salary', salaryPh: 'e.g. $120K–$180K',
      location: 'Location', locationPh: 'e.g. San Francisco · Full-time',
      tags: 'Skill Tags', tagsPh: 'Comma-separated, e.g. Python, PyTorch',
      desc: 'Job Description', descPh: 'Describe the role in plain language, or let AI write it…',
      aiBtn: '✨ AI Polish',
      aiLoading: 'Generating…',
      submit: '🚀 Publish Job',
      toast: 'Job published ✓',
      required: 'Company name and job title are required.',
    },
    footer: 'Offer-Catcher · AI-powered job matching · Demo · Built with Claude',
    profile: {
      title: 'My Profile', guest: 'Guest User', guestSub: 'Job Seeker',
      settings: 'Settings', langLabel: 'Interface Language', about: 'About',
      aboutDesc: 'Offer-Catcher is an AI-powered job matching tool that helps job seekers find the best-fit positions and receive personalized resume optimization advice.',
      version: 'Version 1.0.0 Beta', applyNote: 'Language changes apply to the next analysis',
      showPreset: 'Show preset jobs',
      myJobs: 'My Job Posts', jobActive: 'Active', jobClosed: 'Closed',
      closeJob: 'Mark as Filled', reopenJob: 'Reopen',
      closedToast: 'Job closed ✓', reopenedToast: 'Job reopened ✓',
      jdmatch: 'JD Fit Analyzer',
      jdmatchDesc: 'Paste any JD to analyze how well your resume fits',
      batch: '📦 Batch Screening (HR)',
      batchDesc: 'Upload many resumes, AI ranks them',
    },
    jdm: {
      title: 'JD Fit Analyzer',
      sub: 'Paste a job description from any platform, upload your resume, and get a deep AI-powered match analysis',
      jdLabel: 'Job Description (JD)',
      jdPh: 'Paste the full job description here…\n\nCopy it from LinkedIn, Indeed, or any company career page',
      clear: 'Clear',
      resumeLabel: 'My Resume',
      uploadHint: '📋 Click to upload your resume',
      analyzeBtn: '🔍 Analyze Fit',
      analyzing: 'Analyzing…',
      requireBoth: 'Please paste a JD and upload your resume first',
      reset: '↺ Analyze Again',
    }
  }
}

// Default-language logic: localStorage value -> fallback to Chinese ('zh')
const savedLocale = localStorage.getItem('oc_locale') || 'zh'

export const i18n = createI18n({
  legacy: false,
  globalInjection: true,
  locale: savedLocale,
  fallbackLocale: 'zh',
  messages
})

export function setLocale(lang) {
  i18n.global.locale.value = lang
  localStorage.setItem('oc_locale', lang)
  document.documentElement.lang = lang === 'zh' ? 'zh-CN' : 'en'
}

document.documentElement.lang = savedLocale === 'zh' ? 'zh-CN' : 'en'
