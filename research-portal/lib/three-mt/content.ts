// Slide: unchanged October 2, 2026 PowerPoint. Speech: author-provided October 11, 2026.
export const SPEECH_TITLE = "A Tiny Electronic Nose for Safer Spaces";
export const SPEECH_PARAGRAPHS: string[] = [
  "Imagine a nose that never sleeps. It could sit in a home, a factory, beside a highway, or inside a future smart city. But this nose is not biological. It is an electronic nose: chemical sensors connected to a tiny AI model.",
  "The idea is simple. Air reaches the sensors. The sensors create a chemical fingerprint. The AI recognizes the pattern and can produce a warning.",
  "But there is a hidden problem. Sensors change. As they age, heat, humidity, contamination, and time can slowly alter the signals they produce.",
  "Think of a piano drifting out of tune. The song has not changed, but the instrument has. An AI model trained on the old sound may still answer with confidence, even when its senses are no longer reliable.",
  "That is exactly what I see in my chronological experiments. One compact baseline model was about 81 percent accurate on an early test batch. On much later sensor data, the same frozen model fell to about 37 percent.",
  "The model did not forget its mathematics. Its world changed.",
  "My research asks a simple question: how can we build a small AI system that notices this change, explains what it is using, and remains trustworthy enough to run beside the sensor on a low-power device?",
  "Why does that matter?",
  "For people, an electronic nose could help monitor indoor air and flag unusual chemical exposure. In factories, it could support earlier detection of leaks or changes in process conditions.",
  "For the environment, networks of small sensors could watch for pollution or toxic releases close to where they happen. And in the future, the same idea could give smart buildings, robots, farms, and cities a dependable sense of smell.",
  "My goal is not simply to make a machine that can smell on day one. I want to build one that can recognize when its own sense of smell is changing—and tell us when we should no longer trust it.",
  "Because trustworthy AI is not just AI that gives an answer. It is AI that knows when the world has changed.",
  "And that is the future I am working toward: tiny, explainable intelligence that can keep watching over people and the environment, even as its sensors grow old."
];
export const SPEECH_SOURCE_PATH = "docs/3mt/speech.txt";
export const SPEECH_ASSET_PATH = "/3mt/Arun_Gharami_FAU_3MT_Speech.txt";
export const SLIDE_ASSET_PATH = "/3mt/Arun_Gharami_FAU_3MT_Updated.pptx";
export const SLIDE_PREVIEW_PATH = "/3mt/Arun_Gharami_FAU_3MT_Preview.png";
export const SLIDE_SOURCE_PATH = "research-portal/public/3mt/Arun_Gharami_FAU_3MT_Updated.pptx";
export const SLIDE_CONTENT = {
  title: "A Tiny Electronic Nose for Safer Spaces",
  subtitle: "Keeping detection reliable as sensors change",
  attribution: "Arun Kumar Gharami | PhD Student, Computer Engineering | Florida Atlantic University | Electrical Engineering and Computer Science",
} as const;
