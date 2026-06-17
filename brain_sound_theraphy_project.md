# Brain Sound Theraphy Project

## 1. 프로젝트 개요

이 프로젝트는 40Hz 청각 자극음을 웹브라우저에서 직접 생성하고 재생하는 간단한 실험용 웹페이지입니다. 별도의 오디오 파일을 미리 준비하지 않고, 브라우저의 Web Audio API를 이용해 사용자가 설정한 주파수와 볼륨, 재생 시간에 맞춰 실시간으로 파형을 생성합니다.

핵심 아이디어는 사람이 듣기 쉬운 캐리어 주파수, 예를 들어 440Hz 사인파를 만들고, 그 소리의 진폭을 40Hz로 빠르게 변화시키는 진폭 변조 방식입니다. 즉, 40Hz 순음을 직접 크게 들려주는 것이 아니라, 가청 주파수의 소리가 초당 40번 커졌다 작아지는 형태의 음원을 생성합니다.

본 프로젝트는 연구, 학습, 프로토타입 제작 목적의 예제이며 의료적 진단이나 치료 목적의 도구가 아닙니다.

## 2. 주요 내용

### 2.1 40Hz 진폭 변조 사운드

프로젝트에서 생성하는 오디오 신호는 다음과 같은 구조를 가집니다.

```text
최종 신호 = 캐리어 신호 * 40Hz 변조 엔벨로프 * 볼륨
```

캐리어 신호는 실제로 귀에 들리는 기본 음정입니다.

```text
carrier = sin(2 * pi * carrierFreq * t)
```

변조 엔벨로프는 0에서 1 사이를 오가도록 만든 40Hz 사인파입니다.

```text
envelope = 0.5 * (1 + sin(2 * pi * modFreq * t - pi / 2))
```

기본 설정에서는 다음 값을 사용합니다.

- 캐리어 주파수: 440Hz
- 변조 주파수: 40Hz
- 볼륨: 20%
- 지속 시간: 10초

### 2.2 웹페이지 기능

현재 `index.html`은 다음 기능을 제공합니다.

- 브라우저에서 40Hz AM 오디오 생성
- 캐리어 주파수 조절
- 변조 주파수 조절
- 볼륨 조절
- 재생 시간 조절
- 재생 및 정지 버튼
- 현재 재생 상태 표시
- 시작/종료 시 짧은 페이드 적용으로 클릭 노이즈 완화

### 2.3 안전 및 사용상 주의

이 프로젝트는 실험용 오디오 생성 예제입니다. 다음 사항을 지키는 것이 좋습니다.

- 처음에는 낮은 볼륨으로 짧게 테스트합니다.
- 불편감, 어지러움, 두통, 이명 등이 느껴지면 즉시 중단합니다.
- 임상적 효과나 치료 효과를 전제로 사용하지 않습니다.
- 청각 질환, 신경계 질환, 광과민성/감각 과민 이력이 있는 경우 전문가와 상의 없이 장시간 사용하지 않습니다.

## 3. 코드 작성 관련 내용

### 3.1 파일 구성

현재 프로젝트는 단일 HTML 파일로 구성되어 있습니다.

```text
index.html
```

외부 라이브러리나 빌드 도구가 필요하지 않습니다. HTML, CSS, JavaScript가 한 파일 안에 포함되어 있으므로 브라우저에서 바로 열 수 있습니다.

### 3.2 HTML 구조

HTML은 크게 세 부분으로 구성됩니다.

- 헤더: 제목, 설명, 재생 상태 표시
- 컨트롤 영역: 주파수, 볼륨, 재생 시간 슬라이더
- 액션 영역: 재생/정지 버튼과 주의 문구

주요 입력 컨트롤은 다음과 같습니다.

```html
<input id="carrier" type="range" min="120" max="880" step="1" value="440">
<input id="mod" type="range" min="1" max="80" step="1" value="40">
<input id="volume" type="range" min="0" max="70" step="1" value="20">
<input id="duration" type="range" min="1" max="60" step="1" value="10">
```

### 3.3 CSS 스타일

CSS는 별도 프레임워크 없이 작성되었습니다. 화면 중앙에 단일 패널을 배치하고, 모바일 화면에서는 컨트롤을 한 줄씩 쌓이도록 반응형 처리를 했습니다.

주요 스타일 방향은 다음과 같습니다.

- 단순한 실험 도구처럼 보이도록 절제된 레이아웃 적용
- 버튼과 슬라이더는 사용 목적이 명확하게 보이도록 구성
- 모바일에서도 텍스트와 컨트롤이 겹치지 않도록 반응형 처리

### 3.4 JavaScript 오디오 생성 흐름

오디오 생성과 재생의 핵심 함수는 `createAmBuffer()`와 `playSound()`입니다.

`createAmBuffer()`는 현재 브라우저의 오디오 샘플레이트를 기준으로 PCM 샘플을 직접 채웁니다.

```js
function createAmBuffer(context, duration, carrierFreq, modFreq, volume) {
  const sampleRate = context.sampleRate;
  const frameCount = Math.floor(sampleRate * duration);
  const buffer = context.createBuffer(1, frameCount, sampleRate);
  const samples = buffer.getChannelData(0);

  for (let i = 0; i < frameCount; i += 1) {
    const t = i / sampleRate;
    const carrier = Math.sin(2 * Math.PI * carrierFreq * t);
    const envelope = 0.5 * (1 + Math.sin((2 * Math.PI * modFreq * t) - (Math.PI / 2)));

    samples[i] = carrier * envelope * volume;
  }

  return buffer;
}
```

실제 코드에서는 시작과 끝에 짧은 페이드를 추가해 갑작스러운 팝 노이즈를 줄였습니다.

`playSound()`는 다음 순서로 동작합니다.

1. 기존 재생 중인 소리를 정지합니다.
2. `AudioContext`를 생성하거나 재사용합니다.
3. 사용자가 설정한 캐리어 주파수, 변조 주파수, 볼륨, 지속 시간을 읽습니다.
4. `AudioBufferSourceNode`를 생성합니다.
5. 생성한 AM 오디오 버퍼를 연결하고 재생합니다.
6. 재생이 끝나면 상태를 정지로 되돌립니다.

### 3.5 브라우저 오디오 정책 대응

대부분의 최신 브라우저는 사용자의 명시적 동작 없이 자동으로 소리를 재생하지 못하게 제한합니다. 따라서 이 프로젝트는 페이지 로드 시 자동 재생하지 않고, 사용자가 `재생` 버튼을 누른 뒤 `AudioContext`를 시작합니다.

```js
if (audioContext.state === "suspended") {
  await audioContext.resume();
}
```

### 3.6 재생 상태 관리

재생 중 사용자가 다시 재생 버튼을 누르거나 정지 버튼을 누르는 경우를 고려해, 현재 재생 중인 소스만 상태를 변경하도록 처리했습니다.

```js
currentSource.onended = () => {
  if (source === currentSource) {
    clearTimeout(timeoutId);
    source = null;
    setStatus(false);
  }
};
```

이 처리는 이전 소스의 종료 이벤트가 새로 시작된 재생 상태를 잘못 바꾸는 상황을 방지합니다.

## 4. 향후 확장 아이디어

추가로 확장할 수 있는 기능은 다음과 같습니다.

- WAV 파일 다운로드 기능
- 좌우 채널을 분리한 스테레오/바이노럴 모드
- 변조 파형 선택: 사인파, 사각파, 삼각파
- 프리셋 저장 기능
- 재생 중 실시간 파형 시각화
- 세션 타이머 및 사용 기록
- 음압 보정 및 장비별 출력 안내

## 5. 결론

이 프로젝트는 40Hz 진폭 변조 청각 자극음을 웹에서 직접 생성하는 가장 단순한 형태의 프로토타입입니다. 파이썬에서 `numpy` 배열로 파형을 만든 뒤 재생하는 방식과 같은 원리를 브라우저 환경으로 옮긴 것이며, 현재 구현은 별도 서버나 오디오 파일 없이 단일 HTML 파일만으로 작동합니다.

다만 임상적 의미의 40Hz 자극은 단순 코드 생성만으로 보장되지 않습니다. 실제 연구 수준의 자극에는 음압, 재생 장비, 주파수 검증, 피험자 안전, 실험 설계가 함께 필요합니다.
