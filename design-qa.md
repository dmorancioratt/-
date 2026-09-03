# 三端驾驶舱设计 QA

## 最终结论

通过。企业端、个人端、管理员端在目标宽屏和 1366px 中等宽度下均无横向溢出、遮挡、裁切或不可达操作；三端采用同一深空蓝设计系统，但保留了明显不同的信息架构和核心视觉。

## 验证基线

| 端 | 视觉参考 | 参考尺寸 | 实现截图 |
| --- | --- | ---: | --- |
| 企业端 | `C:/Users/wwcc1/AppData/Local/Temp/tech-blue-dashboard-demos/vue-big-screen.gif` | 1920×1080 | `docs/qa/hr-dashboard.png` |
| 个人端 | `C:/Users/wwcc1/AppData/Local/Temp/tech-blue-dashboard-demos/threejs-demo.png` | 2241×1148 | `docs/qa/candidate-dashboard.png` |
| 管理端 | `C:/Users/wwcc1/AppData/Local/Temp/tech-blue-dashboard-demos/033.gif` | 1080×524 | `docs/qa/admin-dashboard.png` |

验证状态：登录后的 `/overview`；分别使用学生、企业、管理员角色。主视口为 1920×1080，补充验证 1366×768。数据使用当前本地数据库及 API 返回值，并验证浏览器本地快照优先加载、点击“更新数据”后再刷新。

## 对比证据

- 整页并排对比：`docs/qa/hr-comparison.png`、`docs/qa/candidate-comparison.png`、`docs/qa/admin-comparison.png`
- 右侧信息区专项检查：`docs/qa/hr-right-crop.png`、`docs/qa/candidate-right-crop.png`、`docs/qa/admin-right-crop.png`
- 管理端 1366px 回归：`docs/qa/admin-dashboard-1366.png`

## 设计映射

- 企业端沿用标准科技蓝大屏的高密度看板语言，核心改造成岗位筛选、招聘漏斗、供需关系网、紧缺技能和候选人短名单。
- 个人端将 Three.js 城市场景改造成“职业技能城市”，建筑高度表达能力水平，颜色表达已掌握、成长中和待补齐状态，并支持节点聚焦。
- 管理端将 3D 地球改造成可信知识核心，围绕数据源、事实校验、风险事件、模型服务和治理工作流形成闭环。
- 全局移除了动态背景视频、流动虚线、绿色蒙版、昼夜切换和数据库连接标签，改为静态深空蓝底纹及轻量 WebGL 主视觉。

## 迭代记录

1. 初版检查发现旧外壳仍使用全局动态装饰、共享同构布局和较小字号，属于 P1 视觉与性能问题。已重构主布局、抽取驾驶舱设计令牌并为三端建立不同页面结构。
2. 首次整页截图中工具预览看似缺少右栏，按 P2 裁切风险处理。通过 DOM 几何、页面宽度和右侧专项裁图确认右栏位于视口内，页面无横向溢出，无需牺牲中区信息密度。
3. 在 1366×768 下复测，`htmlScrollWidth === htmlClientWidth`，导航、KPI、三列主体和下方模块均保持完整。

## 缺陷分级

- P0：无
- P1：无
- P2：无
- P3：ECharts 在部分图表打印 `alignTicks` 可读性提示，不影响渲染、交互或数据正确性；生产构建仍提示 Three.js/ECharts 大包体积，后续可按路由拆包优化首屏加载。

## 功能与工程验证

- 三端数据刷新按钮、岗位筛选、技能聚焦、风险列表和 3D 视角交互可用。
- 页面快照会跨路由和刷新保留，只有用户主动点击更新时才重新请求。
- 前端生产构建通过。
- 后端测试 24 项全部通过。

---

# 个人成长智能驾驶舱 3D QA（2026-08-25）

## Evidence

- Source visual truth: approved personal growth cockpit reference image
- Implementation screenshot: `growth-cockpit-1920x1080.png`
- Full-view comparison: `growth-cockpit-comparison.png` (source on the left; implementation on the right)
- Desktop viewport: 1920 × 1080, room idle state.
- Narrow desktop viewport: 1366 × 768, room idle state; no horizontal overflow.
- Interaction state checked: AI assistant hover → actual mouse click → camera focus → AI overlay; overlay close → room return.

## Findings

- No actionable P0/P1/P2 findings for the agreed build target. The implementation keeps the source image's dark metallic enclosure, electric-blue structural lighting, left/center/right station hierarchy, and central control zone while using the supplied seven independent GLB assets as the real interactive content.
- The supplied GLBs intentionally differ from the illustration's bespoke wall screens, desk electronics, chair, plants, and trophy props. The scene compensates with wall stations, recessed panels, floor docks, edge rails, a central desk silhouette, and restrained holographic surfaces rather than creating fake stand-in assets.

## Required Fidelity Surfaces

- Fonts and typography: readable Chinese labels use the existing project font stack with a compact technical readout; labels remain legible at both tested desktop widths.
- Spacing and layout rhythm: models occupy distinct left, upper-center, upper-right, lower-right, and center stations; the panel retains room visibility instead of covering the whole scene.
- Colors and visual tokens: black-blue metallic base, cyan-blue edge rails, low-opacity holographic panels, and restrained bloom follow the source's visual hierarchy.
- Image quality and asset fidelity: all visible functional objects are optimized supplied GLBs; no placeholder image assets replace them.
- Copy and content: Chinese module labels and English subtitles correspond to the mapped business panels.

## Focused Comparison

No focused crop was required: the provided image is a concept illustration rather than a pixel-identical screen target, and the acceptance criteria are the room composition plus working 3D interaction. The full-view comparison exposes both the intentional asset differences and the shared spatial direction.

## Patches Made Since Previous Review

- Added a structured lab shell, recessed wall stations, floor docks, central control desk silhouette, blue rails, and subtle emissive pulses.
- Tuned camera framing and model label offsets.
- Made camera focus lock interaction and open the overlay from the completed focus sequence; closing the overlay restores the default camera and controls.
- Added model-load fallback messaging and cleanup for renderer resources.

## Implementation Checklist

- [x] Seven GLBs load as independent selectable scene devices.
- [x] Hover gives outline, lift, scale, pointer, and contextual label feedback.
- [x] Click focuses camera and opens mapped overlay panel.
- [x] Close restores the cockpit.
- [x] 1920 × 1080 and 1366 × 768 views checked.

## Follow-up Polish

- [P3] A later art pass could introduce purpose-built wall-screen, chair, and plant GLBs if closer illustration fidelity is needed.

final result: passed
