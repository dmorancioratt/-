<template>
  <section class="image-cabin" aria-label="个人学习成长仓">
    <div class="image-cabin__canvas">
      <img class="image-cabin__image" src="/growth-cabin-reference.png" alt="个人学习成长仓模块总览" />
      <button
        v-for="item in modules"
        :key="item.id"
        type="button"
        class="image-cabin__zone"
        :class="`image-cabin__zone--${item.id}`"
        :style="zoneStyle(item)"
        :aria-label="`打开${item.label}`"
        @click="emit('select', item.id)"
      >
        <span class="image-cabin__dash"></span>
        <span class="image-cabin__tag"><b>{{ item.index }}</b>{{ item.label }}</span>
      </button>
    </div>
  </section>
</template>

<script setup lang="ts">
type ModuleId = 'match' | 'radar' | 'jobs' | 'ai-suggest' | 'weekly-plan' | 'interview' | 'timeline' | 'path' | 'avatar'
type ModuleZone = { id: ModuleId; label: string; index: string; x: number; y: number; width: number; height: number }

const emit = defineEmits<{ select: [id: ModuleId] }>()

const modules: ModuleZone[] = [
  { id: 'radar',       label: '能力图谱', index: '02', x: 7.5,  y: 10,   width: 27, height: 29 },
  { id: 'path',        label: '学习路径', index: '03', x: 38,   y: 10,   width: 27, height: 25 },
  { id: 'timeline',    label: '成长档案', index: '04', x: 67,   y: 12,   width: 25, height: 19 },
  { id: 'weekly-plan', label: '计划日历', index: '05', x: 65,   y: 29,   width: 30, height: 30 },
  { id: 'jobs',        label: '资源库',   index: '06', x: 7.5,  y: 43,   width: 20, height: 31 },
  { id: 'interview',   label: '成就墙',   index: '07', x: 68,   y: 55,   width: 28, height: 25 },
  { id: 'avatar',      label: '智能桌台', index: '01', x: 38,   y: 40,   width: 25, height: 27 },
  { id: 'ai-suggest',  label: 'AI 助手',  index: '08', x: 28,   y: 38,   width: 15, height: 24 },
  { id: 'match',       label: '数据看板', index: '09', x: 18,   y: 75.5, width: 36, height: 16 },
]

function zoneStyle(item: ModuleZone) {
  return { left: `${item.x}%`, top: `${item.y}%`, width: `${item.width}%`, height: `${item.height}%` }
}
</script>

<style scoped>
.image-cabin { position: absolute; inset: 0; display: grid; place-items: center; overflow: hidden; background: radial-gradient(circle at 50% 46%, #072667 0%, #020715 68%); }
.image-cabin__canvas { position: relative; width: min(100vw, calc(100vh * 1.774)); aspect-ratio: 1672 / 942; overflow: hidden; }
.image-cabin__image { display: block; width: 100%; height: 100%; user-select: none; }
.image-cabin__zone { position: absolute; z-index: 2; display: block; padding: 0; border: 0; border-radius: 10px; background: transparent; cursor: pointer; }
.image-cabin__dash { position: absolute; inset: 0; border: 2px dashed rgba(108, 227, 255, .72); border-radius: 10px; box-shadow: inset 0 0 22px rgba(19, 180, 255, .12), 0 0 15px rgba(11, 149, 255, .12); opacity: .68; transition: .22s ease; pointer-events: none; }
.image-cabin__tag { position: absolute; top: -12px; left: 50%; display: flex; align-items: center; gap: 5px; padding: 3px 8px 3px 4px; border: 1px solid rgba(123, 235, 255, .82); border-radius: 999px; background: rgba(1, 17, 49, .9); box-shadow: 0 0 14px rgba(30, 185, 255, .4); color: #f1fbff; font-size: clamp(8px, .9vw, 14px); font-weight: 800; white-space: nowrap; opacity: 0; transform: translateX(-50%) scale(.92); transition: .22s ease; pointer-events: none; }
.image-cabin__tag b { display: grid; width: clamp(17px, 1.8vw, 28px); height: clamp(17px, 1.8vw, 28px); place-items: center; border-radius: 50%; background: linear-gradient(135deg, #67eaff, #3878ff); box-shadow: 0 0 10px #48cfff; color: #031535; font-size: .75em; }
.image-cabin__zone:hover .image-cabin__dash, .image-cabin__zone:focus-visible .image-cabin__dash { border-color: #d7fbff; background: rgba(40, 211, 255, .12); box-shadow: inset 0 0 34px rgba(34, 209, 255, .24), 0 0 28px rgba(27, 199, 255, .72); opacity: 1; }
.image-cabin__zone:hover .image-cabin__tag, .image-cabin__zone:focus-visible .image-cabin__tag { opacity: 1; transform: translateX(-50%) scale(1.08); box-shadow: 0 0 24px rgba(63, 222, 255, .82); }
.image-cabin__zone:focus-visible { outline: 0; }
.image-cabin__zone--ai-suggest { z-index: 4; }
@media (max-width: 700px) { .image-cabin__tag { top: -9px; padding: 2px 5px 2px 3px; gap: 3px; } .image-cabin__dash { border-width: 1px; border-radius: 5px; } }
</style>
