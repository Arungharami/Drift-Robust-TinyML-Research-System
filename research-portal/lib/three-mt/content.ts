// Verbatim source material for the /3mt page, copied from the actual files the author
// submitted for the FAU 2026 Three Minute Thesis competition:
//   docs/3mt/speech.txt (speech transcript)
//   research-portal/public/3mt/Arun_Gharami_FAU_3MT_2026_Single_Slide.pptx (single slide)
// Nothing here is invented — this module only reproduces what already exists. If either
// source file is ever removed, the content below should be removed too, not replaced with
// paraphrased or fabricated text (see AGENTS.md: never invent or quote a speech that doesn't exist).

export const SPEECH_TITLE = "3MT Speech — FAU 2026";

/** One entry per paragraph, in original order, exactly as written in docs/3mt/speech.txt. */
export const SPEECH_PARAGRAPHS: string[] = [
  "Imagine opening your refrigerator and smelling milk that has gone bad.",
  "Before you read the date, your nose warns you.",
  "Now imagine giving that ability to a machine.",
  "An electronic nose uses chemical sensors and artificial intelligence to recognize patterns in gases. These systems could help monitor food, detect hazardous chemicals, and support environmental or health applications.",
  "But there is a hidden problem.",
  "The nose changes.",
  "Electronic sensors age. Temperature and humidity affect them. Their signals slowly shift, even when the chemical being measured has not changed. Scientists call this sensor drift.",
  "And when the sensor changes, an AI model trained yesterday may not understand the world tomorrow.",
  "In this research, use an electronic-nose dataset collected over three years. Trained four baseline AI models on the earliest sensor readings and tested them as time moved forward.",
  "The result was striking.",
  "Between Month 3 and Month 36, every model lost roughly 35 to 49 percentage points of accuracy. In one lightweight model, accuracy fell from about 81 percent to 37 percent.",
  "That means an AI system can look excellent when it is first built—and become unreliable simply because its sensors grow older.",
  "So my research asks a different question:",
  "Can we build small AI systems that remain trustworthy when their sensors and environment change?",
  "Developing a drift-aware, explainable TinyML research pipeline. Instead of randomly mixing old and new sensor data, I evaluate models in chronological order, the way they would experience the real world. I examine not only whether a prediction is correct, but also whether the reasons behind that prediction stay stable as the sensors drift. Then I study which lightweight models are realistic candidates for resource-constrained embedded devices.",
  "This matters because the future of AI is not only in giant data centers.",
  "It is moving into factories, farms, wearable devices, environmental monitors, and small sensors that may operate for months or years.",
  "For trustworthy AI, high accuracy on day one is not enough.",
  "We need confidence that the system will still deserve our trust on day one thousand.",
  "An electronic nose how to recognize when its world has changed.",
  "Because when AI gains a sense of smell, it should not forget how to use it.",
];

export const SPEECH_SOURCE_PATH = "docs/3mt/speech.txt";
export const SLIDE_ASSET_PATH = "/3mt/Arun_Gharami_FAU_3MT_2026_Single_Slide.pptx";
export const SLIDE_SOURCE_PATH = "research-portal/public/3mt/Arun_Gharami_FAU_3MT_2026_Single_Slide.pptx";

/** Verbatim text content extracted from the single slide (one shape per entry, in slide order). */
export const SLIDE_CONTENT = {
  title: "WHEN AI LOSES ITS SENSE OF SMELL",
  subtitle: "Electronic noses can learn. Sensors can drift.",
  panelA: { label: "MONTH 3", stat: "81%", caption: "baseline accuracy" },
  panelB: { label: "MONTH 36", stat: "37%", caption: "same baseline, later sensors" },
  driftLabel: "SENSOR DRIFT",
  driftCaption: "the world changes\nwhile the model stays the same",
  statLine: "Across 4 baseline models:  35–49 percentage-point accuracy loss  (Month 3 → Month 36)",
  goalLine: "Research goal: build small AI that stays trustworthy as sensors change.",
  attribution: "Arun Kumar Gharami  |  Ph.D. in Computer Engineering  |  Florida Atlantic University",
} as const;
