<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'

const HOT = ['hot-r', 'hot-o', 'hot-y']
let flashInterval: ReturnType<typeof setTimeout> | null = null

function generatePins() {
  document.querySelectorAll('.qfp-pins').forEach((row) => {
    const n = parseInt((row as HTMLElement).dataset.count || '5')
    for (let i = 0; i < n; i++) {
      const p = document.createElement('div')
      p.className = 'pin'
      row.appendChild(p)
    }
  })
}

function flashPin() {
  const chips = document.querySelectorAll('.qfp-wrap')
  if (!chips.length) return

  const chip = chips[Math.floor(Math.random() * chips.length)] as HTMLElement
  const pins = chip.querySelectorAll('.pin')
  if (!pins.length) return

  const burst = 1 + Math.floor(Math.random() * 3)
  for (let b = 0; b < burst; b++) {
    const pin = pins[Math.floor(Math.random() * pins.length)] as HTMLElement
    const cls = HOT[Math.floor(Math.random() * HOT.length)]
    setTimeout(() => {
      pin.classList.add(cls)
      setTimeout(() => pin.classList.remove(cls), 120 + Math.random() * 280)
    }, b * 60)
  }
}

function scheduleFlash() {
  flashPin()
  flashInterval = setTimeout(scheduleFlash, 180 + Math.random() * 200)
}

onMounted(() => {
  generatePins()
  scheduleFlash()
})

onUnmounted(() => {
  if (flashInterval) {
    clearTimeout(flashInterval)
  }
})
</script>

<template>
  <div class="pcb-background">
    <div class="pcb-grid"></div>

    <svg class="traces" viewBox="0 0 1440 900" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
      <path class="tr tra" d="M0,192 H160 V128 H384 V192 H640 V256 H864 V192 H1104 V128 H1280 V192 H1440"/>
      <path class="tr tra" d="M160,192 V448 H96  V512 H224 V576 H128 V704"/>
      <path class="tr trb" d="M384,128 V64  H544 V32"/>
      <path class="tr tra" d="M640,256 V352 H576 V448 H672 V544 H592 V672 H704 V784"/>
      <path class="tr tra" d="M864,192 V320 H800 V448 H896 V544 H816 V672 H944 V768"/>
      <path class="tr trb" d="M1104,128 V64  H1200 V32  H1360"/>
      <path class="tr tra" d="M1280,192 V352 H1360 V464 H1264 V576 H1376 V704 H1296 V816"/>
      <path class="tr trb" d="M0,464 H96  V384 H224"/>
      <path class="tr trc" d="M224,576 H352 V624 H496 V560 H640"/>
      <path class="tr trb" d="M704,784 H864 V720 H944"/>
      <path class="tr trc" d="M0,704 H128 V768 H288 V704 H464 V768 H608 V704 H752"/>
      <path class="tr trb" d="M896,544 H992 V624 H1104 V544"/>
      <path class="tr trc" d="M1104,544 H1200 V480 H1264"/>
      <path class="tr trb" d="M576,448 H480 V528 H400 V448"/>
      <path class="tr trc" d="M400,448 H320 V512 H240 V448"/>
      <path class="tr trb" d="M864,320 H944 V256 H1024 V192"/>
      <path class="pulse pu1" d="M0,192 H160 V128 H384 V192 H640 V256 H864 V192 H1104 V128 H1280 V192 H1440"/>
      <path class="pulse pu2" d="M640,256 V352 H576 V448 H672 V544 H592 V672 H704 V784"/>
      <path class="pulse pu3" d="M0,704 H128 V768 H288 V704 H464 V768 H608 V704 H752"/>
      <path class="pulse pu4" d="M864,192 V320 H800 V448 H896 V544 H816 V672 H944 V768"/>
    </svg>

    <div class="node" style="width:8px;height:8px;top:188px;left:156px;animation-delay:0s"></div>
    <div class="node" style="width:8px;height:8px;top:124px;left:380px;animation-delay:.7s"></div>
    <div class="node" style="width:8px;height:8px;top:252px;left:636px;animation-delay:1.4s"></div>
    <div class="node" style="width:8px;height:8px;top:188px;left:860px;animation-delay:.3s"></div>
    <div class="node" style="width:6px;height:6px;top:124px;left:1100px;animation-delay:2.1s"></div>
    <div class="node" style="width:8px;height:8px;top:188px;left:1276px;animation-delay:1.0s"></div>
    <div class="node" style="width:6px;height:6px;top:348px;left:572px;animation-delay:1.8s"></div>
    <div class="node" style="width:6px;height:6px;top:316px;left:796px;animation-delay:.5s"></div>
    <div class="node" style="width:8px;height:8px;top:444px;left:668px;animation-delay:2.5s"></div>
    <div class="node" style="width:6px;height:6px;top:444px;left:892px;animation-delay:1.2s"></div>
    <div class="node" style="width:6px;height:6px;top:700px;left:124px;animation-delay:.2s"></div>
    <div class="node" style="width:8px;height:8px;top:700px;left:460px;animation-delay:2.8s"></div>
    <div class="node" style="width:6px;height:6px;top:700px;left:748px;animation-delay:1.1s"></div>
    <div class="node" style="width:6px;height:6px;top:540px;left:988px;animation-delay:0.6s"></div>

    <div class="qfp-wrap" style="top:262px;left:28px;">
      <div class="qfp-body" style="width:96px;height:96px;">
        <div class="qfp-notch"></div>
        <div class="qfp-pins top" data-count="7"></div>
        <div class="qfp-pins bottom" data-count="7"></div>
        <div class="qfp-pins left" data-count="7"></div>
        <div class="qfp-pins right" data-count="7"></div>
        <div class="qfp-inner">
          <span class="qfp-type">Processor</span>
          <span class="qfp-name">CPU</span>
          <span class="qfp-id">i9-14900K</span>
        </div>
      </div>
    </div>

    <div class="qfp-wrap" style="top:240px;left:1040px;">
      <div class="qfp-body" style="width:120px;height:120px;">
        <div class="qfp-notch"></div>
        <div class="qfp-pins top" data-count="9"></div>
        <div class="qfp-pins bottom" data-count="9"></div>
        <div class="qfp-pins left" data-count="9"></div>
        <div class="qfp-pins right" data-count="9"></div>
        <div class="qfp-inner">
          <span class="qfp-type">Graphics</span>
          <span class="qfp-name">GPU</span>
          <span class="qfp-id">RTX-4090</span>
        </div>
      </div>
    </div>

    <div class="qfp-wrap" style="top:48px;left:448px;">
      <div class="qfp-body" style="width:80px;height:80px;">
        <div class="qfp-notch"></div>
        <div class="qfp-pins top" data-count="5"></div>
        <div class="qfp-pins bottom" data-count="5"></div>
        <div class="qfp-pins left" data-count="5"></div>
        <div class="qfp-pins right" data-count="5"></div>
        <div class="qfp-inner">
          <span class="qfp-type">Memory</span>
          <span class="qfp-name">RAM</span>
          <span class="qfp-id">DDR5</span>
        </div>
      </div>
    </div>

    <div class="qfp-wrap" style="top:560px;left:480px;">
      <div class="qfp-body" style="width:88px;height:88px;">
        <div class="qfp-notch"></div>
        <div class="qfp-pins top" data-count="6"></div>
        <div class="qfp-pins bottom" data-count="6"></div>
        <div class="qfp-pins left" data-count="6"></div>
        <div class="qfp-pins right" data-count="6"></div>
        <div class="qfp-inner">
          <span class="qfp-type">Chipset</span>
          <span class="qfp-name">PCH</span>
          <span class="qfp-id">Z790</span>
        </div>
      </div>
    </div>

    <div class="qfp-wrap" style="top:480px;left:800px;">
      <div class="qfp-body" style="width:72px;height:72px;">
        <div class="qfp-notch"></div>
        <div class="qfp-pins top" data-count="5"></div>
        <div class="qfp-pins bottom" data-count="5"></div>
        <div class="qfp-pins left" data-count="5"></div>
        <div class="qfp-pins right" data-count="5"></div>
        <div class="qfp-inner">
          <span class="qfp-type">Network</span>
          <span class="qfp-name">NIC</span>
          <span class="qfp-id">2.5GbE</span>
        </div>
      </div>
    </div>

    <div class="qfp-wrap" style="top:112px;left:816px;">
      <div class="qfp-body" style="width:72px;height:72px;">
        <div class="qfp-notch"></div>
        <div class="qfp-pins top"></div>
        <div class="qfp-pins bottom"></div>
        <div class="qfp-pins left"></div>
        <div class="qfp-pins right"></div>
        <div class="qfp-inner">
          <span class="qfp-type">Firmware</span>
          <span class="qfp-name">BIOS</span>
          <span class="qfp-id">SPI 128M</span>
        </div>
      </div>
    </div>

    <div class="qfp-wrap" style="top:48px;left:1168px;">
      <div class="qfp-body" style="width:80px;height:80px;">
        <div class="qfp-notch"></div>
        <div class="qfp-pins top"></div>
        <div class="qfp-pins bottom"></div>
        <div class="qfp-pins left"></div>
        <div class="qfp-pins right"></div>
        <div class="qfp-inner">
          <span class="qfp-type">Interface</span>
          <span class="qfp-name">USB</span>
          <span class="qfp-id">USB4 TB4</span>
        </div>
      </div>
    </div>

    <div class="qfp-wrap" style="top:400px;left:1248px;">
      <div class="qfp-body" style="width:80px;height:80px;">
        <div class="qfp-notch"></div>
        <div class="qfp-pins top" data-count="5"></div>
        <div class="qfp-pins bottom" data-count="5"></div>
        <div class="qfp-pins left" data-count="5"></div>
        <div class="qfp-pins right" data-count="5"></div>
        <div class="qfp-inner">
          <span class="qfp-type">Bus</span>
          <span class="qfp-name">PCIe</span>
          <span class="qfp-id">GEN5 x16</span>
        </div>
      </div>
    </div>

    <div class="dip-wrap" style="top:352px;left:480px;">
      <div class="dip-body" style="width:88px;--dp:8px;--dh:40px;">
        <div class="dip-label">
          <span class="dip-type">Storage</span>
          <span class="dip-name">SSD</span>
          <span class="dip-model">NVMe PCIe 4.0</span>
        </div>
      </div>
    </div>

    <div class="dip-wrap" style="top:432px;left:224px;">
      <div class="dip-body" style="width:80px;--dp:7px;--dh:34px;">
        <div class="dip-label">
          <span class="dip-type">Power</span>
          <span class="dip-name">PSU</span>
          <span class="dip-model">VRM 16-Ph</span>
        </div>
      </div>
    </div>

    <div class="dip-wrap" style="top:608px;left:832px;">
      <div class="dip-body" style="width:80px;--dp:7px;--dh:34px;">
        <div class="dip-label">
          <span class="dip-type">Audio</span>
          <span class="dip-name">DAC</span>
          <span class="dip-model">ALC4080</span>
        </div>
      </div>
    </div>

    <div class="dip-wrap" style="top:632px;left:128px;">
      <div class="dip-body" style="width:80px;--dp:7px;--dh:32px;">
        <div class="dip-label">
          <span class="dip-type">Storage</span>
          <span class="dip-name">HDD</span>
          <span class="dip-model">SATA III</span>
        </div>
      </div>
    </div>

    <div class="dip-wrap" style="top:704px;left:624px;">
      <div class="dip-body" style="width:80px;--dp:6px;--dh:28px;">
        <div class="dip-label">
          <span class="dip-type">Sensor</span>
          <span class="dip-name">TEMP</span>
          <span class="dip-model">TMP117</span>
        </div>
      </div>
    </div>

    <div class="passive resistor" style="top:196px;left:480px;"><span class="plbl">R14</span></div>
    <div class="passive resistor" style="top:278px;left:256px;"><span class="plbl">R22</span></div>
    <div class="passive resistor" style="top:416px;left:656px;"><span class="plbl">R07</span></div>
    <div class="passive resistor" style="top:656px;left:1008px;"><span class="plbl">R33</span></div>
    <div class="passive resistor" style="top:752px;left:368px;"><span class="plbl">R41</span></div>
    <div class="passive resistor" style="top:86px;left:672px;"><span class="plbl">R05</span></div>
    <div class="passive capacitor" style="top:400px;left:160px;"><span class="plbl">C3</span></div>
    <div class="passive capacitor" style="top:544px;left:752px;"><span class="plbl">C8</span></div>
    <div class="passive capacitor" style="top:672px;left:1104px;"><span class="plbl">C14</span></div>
    <div class="passive capacitor" style="top:192px;left:1040px;"><span class="plbl">C2</span></div>
    <div class="passive capacitor" style="top:64px;left:288px;"><span class="plbl">C6</span></div>

    <div class="vignette"></div>
    <div class="scanlines"></div>
  </div>
</template>

<style scoped>
.pcb-background {
  position: fixed;
  inset: 0;
  z-index: 0;
  overflow: hidden;
  opacity: var(--pcb-bg-opacity, 0.85);
}

.pcb-grid {
  position: absolute;
  inset: 0;
  z-index: 1;
  background-image:
    linear-gradient(var(--pcb-grid) 1px, transparent 1px),
    linear-gradient(90deg, var(--pcb-grid) 1px, transparent 1px);
  background-size: 16px 16px;
}

.pcb-grid::after {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(70,95,125,0.07) 1px, transparent 1px),
    linear-gradient(90deg, rgba(70,95,125,0.07) 1px, transparent 1px);
  background-size: 64px 64px;
}

.traces {
  position: absolute;
  inset: 0;
  z-index: 2;
  pointer-events: none;
}

.tr {
  fill: none;
  stroke-linecap: square;
  stroke-linejoin: miter;
}

.tra {
  stroke: rgba(90,90,90,0.22);
  stroke-width: 2;
}

.trb {
  stroke: rgba(90,90,90,0.13);
  stroke-width: 1.5;
}

.trc {
  stroke: rgba(100,100,100,0.18);
  stroke-width: 2;
}

.pulse {
  fill: none;
  stroke-linecap: square;
  opacity: 0;
}

.pu1 {
  stroke: #4488ff;
  stroke-width: 3;
  animation: da1 7s linear 0s infinite;
}

.pu2 {
  stroke: #22ccaa;
  stroke-width: 2;
  animation: da2 9s linear 2s infinite;
}

.pu3 {
  stroke: #cc44ff;
  stroke-width: 2;
  animation: da3 8s linear 4.5s infinite;
}

.pu4 {
  stroke: #4488ff;
  stroke-width: 2;
  animation: da4 11s linear 1s infinite;
}

@keyframes da1 {
  0% { stroke-dasharray: 0 2400; stroke-dashoffset: 0; opacity: 0; }
  4% { opacity: .85; }
  72% { stroke-dasharray: 16 2400; stroke-dashoffset: -880; opacity: .75; }
  100% { stroke-dasharray: 0 2400; stroke-dashoffset: -2400; opacity: 0; }
}

@keyframes da2 {
  0% { stroke-dasharray: 0 1800; stroke-dashoffset: 0; opacity: 0; }
  4% { opacity: .75; }
  72% { stroke-dasharray: 16 1800; stroke-dashoffset: -720; opacity: .65; }
  100% { stroke-dasharray: 0 1800; stroke-dashoffset: -1800; opacity: 0; }
}

@keyframes da3 {
  0% { stroke-dasharray: 0 2000; stroke-dashoffset: 0; opacity: 0; }
  4% { opacity: .70; }
  72% { stroke-dasharray: 16 2000; stroke-dashoffset: -800; opacity: .60; }
  100% { stroke-dasharray: 0 2000; stroke-dashoffset: -2000; opacity: 0; }
}

@keyframes da4 {
  0% { stroke-dasharray: 0 1600; stroke-dashoffset: 0; opacity: 0; }
  4% { opacity: .60; }
  72% { stroke-dasharray: 16 1600; stroke-dashoffset: -640; opacity: .50; }
  100% { stroke-dasharray: 0 1600; stroke-dashoffset: -1600; opacity: 0; }
}

.node {
  position: absolute;
  z-index: 3;
  background: var(--pcb-node);
  border: 2px solid rgba(80,80,80,0.35);
  animation: npulse 3.5s steps(4) infinite;
}

@keyframes npulse {
  0%,100% { opacity: .4; }
  25% { opacity: .9; }
  50% { opacity: .5; }
  75% { opacity: 1; }
}

.qfp-wrap {
  position: absolute;
  z-index: 5;
}

.qfp-body {
  position: relative;
  background: var(--pcb-chip-bg);
  border: 2px solid var(--pcb-chip-bdr);
  box-shadow: 3px 3px 0 rgba(80,80,80,0.15), 6px 6px 0 rgba(80,80,80,0.07);
}

.qfp-pins {
  position: absolute;
  display: flex;
  gap: 0;
}

.qfp-pins.top, .qfp-pins.bottom {
  flex-direction: row;
  left: 8px;
  width: calc(100% - 16px);
  justify-content: space-between;
}

.qfp-pins.top { top: -7px; }
.qfp-pins.bottom { bottom: -7px; }

.qfp-pins.left, .qfp-pins.right {
  flex-direction: column;
  top: 8px;
  height: calc(100% - 16px);
  justify-content: space-between;
}

.qfp-pins.left { left: -7px; }
.qfp-pins.right { right: -7px; }

:deep(.pin) {
  background: var(--pcb-chip-pin);
  flex-shrink: 0;
  transition: background 0.06s, box-shadow 0.06s;
  width: 5px;
  height: 7px;
}

:deep(.qfp-pins.left .pin),
:deep(.qfp-pins.right .pin) {
  width: 7px;
  height: 5px;
}

:deep(.pin.hot-r) {
  background: #ff2200 !important;
  box-shadow: 0 0 6px 2px rgba(255,34,0,0.60);
}

:deep(.pin.hot-o) {
  background: #ff8800 !important;
  box-shadow: 0 0 6px 2px rgba(255,136,0,0.55);
}

:deep(.pin.hot-y) {
  background: #ffcc00 !important;
  box-shadow: 0 0 5px 2px rgba(255,204,0,0.50);
}

.qfp-inner {
  padding: 6px 7px 5px;
  display: flex;
  flex-direction: column;
  gap: 3px;
  user-select: none;
}

.qfp-type {
  font-size: 4.5px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--pcb-chip-sub);
}

.qfp-name {
  font-size: 10px;
  color: var(--pcb-chip-text);
  letter-spacing: 0.04em;
  text-transform: uppercase;
  line-height: 1.1;
  text-shadow: 1px 1px 0 rgba(255,255,255,0.6);
}

.qfp-id {
  font-size: 4px;
  color: var(--pcb-chip-sub);
  letter-spacing: 0.10em;
}

.qfp-notch {
  position: absolute;
  top: 3px;
  left: 3px;
  width: 6px;
  height: 6px;
  border-right: 2px solid var(--pcb-chip-bdr);
  border-bottom: 2px solid var(--pcb-chip-bdr);
  opacity: 0.5;
}

.dip-wrap {
  position: absolute;
  z-index: 5;
}

.dip-body {
  position: relative;
  background: var(--pcb-chip-bg);
  border: 2px solid var(--pcb-chip-bdr);
  box-shadow: 2px 2px 0 rgba(80,80,80,0.13);
}

.dip-body::before, .dip-body::after {
  content: '';
  position: absolute;
  top: var(--dp, 8px);
  height: var(--dh, 40px);
  width: 7px;
  background: repeating-linear-gradient(
    to bottom,
    var(--pcb-chip-pin) 0, var(--pcb-chip-pin) 5px,
    transparent 5px, transparent 10px
  );
}

.dip-body::before { left: -8px; }
.dip-body::after { right: -8px; }

.dip-label {
  padding: 5px 9px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  user-select: none;
}

.dip-type {
  font-size: 4px;
  color: var(--pcb-chip-sub);
  letter-spacing: 0.10em;
  text-transform: uppercase;
}

.dip-name {
  font-size: 8px;
  color: var(--pcb-chip-text);
  text-transform: uppercase;
  line-height: 1.2;
  text-shadow: 1px 1px 0 rgba(255,255,255,0.6);
}

.dip-model {
  font-size: 3.5px;
  color: var(--pcb-chip-sub);
  letter-spacing: 0.08em;
}

.passive {
  position: absolute;
  z-index: 4;
  background: var(--pcb-chip-bg);
  border: 2px solid var(--pcb-chip-bdr);
}

.resistor {
  width: 32px;
  height: 12px;
}

.capacitor {
  width: 12px;
  height: 22px;
}

.passive .plbl {
  position: absolute;
  font-size: 4px;
  color: var(--pcb-chip-sub);
  top: 1px;
  left: 2px;
  white-space: nowrap;
}

.vignette {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 11;
  background: radial-gradient(ellipse at center, transparent 48%, rgba(150,150,150,0.20) 100%);
}

.scanlines {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 12;
  background: repeating-linear-gradient(
    to bottom, transparent 0, transparent 3px,
    rgba(0,0,0,0.025) 3px, rgba(0,0,0,0.025) 4px
  );
}
</style>
