<template>
  <Teleport to="body">
    <div v-if="modelValue" class="overlay" @click.self="$emit('update:modelValue', false)">
      <div class="pp">
        <div class="pp-hdr">
          <span class="pp-htitle">{{ t('profile.title') }}</span>
          <button class="rm" @click="$emit('update:modelValue', false)">✕</button>
        </div>

        <div class="pp-avt-sec">
          <div class="pp-avt">👤</div>
          <div class="pp-aname">{{ t('profile.guest') }}</div>
          <div class="pp-asubt">{{ t('profile.guestSub') }}</div>
        </div>

        <div class="pp-sec">
          <div class="pp-sec-title">{{ t('profile.settings') }}</div>
          <div class="pp-item-lbl">🌐 {{ t('profile.langLabel') }}</div>
          <div class="lang-sw">
            <button :class="['lang-btn', locale === 'zh' && 'act']" @click="switchLang('zh')">
              <span class="lf">🇨🇳</span><span class="lt">中文</span>
            </button>
            <button :class="['lang-btn', locale === 'en' && 'act']" @click="switchLang('en')">
              <span class="lf">🇺🇸</span><span class="lt">English</span>
            </button>
          </div>
        </div>

        <div class="pp-sec">
          <div class="pp-sec-title">{{ t('profile.about') }}</div>
          <div class="pp-app-row">
            <div class="pp-app-icon">🎯</div>
            <div>
              <div class="pp-app-name">Offer-Catcher</div>
              <div class="pp-app-ver">{{ t('profile.version') }}</div>
            </div>
          </div>
          <p class="pp-about">{{ t('profile.aboutDesc') }}</p>
        </div>

        <div class="pp-footer">{{ t('profile.applyNote') }}</div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import { setLocale } from '../i18n.js'

defineProps({ modelValue: { type: Boolean, default: false } })
defineEmits(['update:modelValue'])

const { t, locale } = useI18n()
function switchLang(lang) { setLocale(lang) }
</script>

<style scoped>
.overlay { position: fixed; inset: 0; background: rgba(0,0,0,.48); z-index: 200; display: flex; justify-content: flex-end; }
@keyframes slideIn { from { transform: translateX(100%); } to { transform: translateX(0); } }
.pp { background: #fff; width: 340px; max-width: 100vw; height: 100%; overflow-y: auto; box-shadow: -6px 0 28px rgba(0,0,0,.14); animation: slideIn .26s cubic-bezier(.22,.61,.36,1); }
.pp-hdr { display: flex; align-items: center; justify-content: space-between; padding: 18px 20px; border-bottom: 1px solid #E2E8F0; }
.pp-htitle { font-size: 1rem; font-weight: 800; color: #0F172A; }
.rm { background: none; border: none; width: 28px; height: 28px; border-radius: 6px; cursor: pointer; color: #64748B; font-size: 1rem; }
.rm:hover { background: #FEE2E2; color: #DC2626; }
.pp-avt-sec { text-align: center; padding: 30px 20px 22px; background: linear-gradient(160deg,#FFFBEB,#fff); border-bottom: 1px solid #E2E8F0; }
.pp-avt { width: 72px; height: 72px; background: linear-gradient(135deg,#FFD700,#F0C800); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 2rem; margin: 0 auto 12px; box-shadow: 0 4px 14px rgba(255,215,0,.4); }
.pp-aname { font-weight: 700; color: #0F172A; }
.pp-asubt { font-size: .78rem; color: #94A3B8; margin-top: 3px; }
.pp-sec { padding: 20px; border-bottom: 1px solid #E2E8F0; }
.pp-sec-title { font-size: .68rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: .1em; margin-bottom: 14px; }
.pp-item-lbl { font-size: .85rem; font-weight: 600; color: #0F172A; margin-bottom: 10px; }
.lang-sw { display: flex; gap: 8px; }
.lang-btn { flex: 1; padding: 11px 8px; border: 2px solid #E2E8F0; border-radius: 10px; background: #fff; cursor: pointer; font-weight: 600; color: #64748B; transition: all .2s; text-align: center; }
.lang-btn.act { border-color: #FFD700; background: #FFFBEB; color: #0F172A; box-shadow: 0 2px 10px rgba(255,215,0,.28); }
.lang-btn:hover:not(.act) { border-color: #94A3B8; background: #F8FAFC; }
.lang-btn .lf { display: block; font-size: 1.2rem; margin-bottom: 3px; }
.lang-btn .lt { display: block; font-size: .78rem; }
.pp-app-row { display: flex; align-items: center; gap: 10px; }
.pp-app-icon { width: 36px; height: 36px; background: #FFD700; border-radius: 8px; display: flex; align-items: center; justify-content: center; }
.pp-app-name { font-weight: 700; color: #0F172A; }
.pp-app-ver { font-size: .76rem; color: #94A3B8; }
.pp-about { font-size: .84rem; color: #64748B; line-height: 1.7; margin-top: 12px; }
.pp-footer { text-align: center; padding: 20px; font-size: .76rem; color: #94A3B8; }
</style>
