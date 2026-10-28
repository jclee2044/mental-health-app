# Research supporting the prototype design

Reviewed October 15, 2026 for Part 3.1. The assignment's R1–R4 and D1–D6 findings remain the primary requirements. These additional studies and official resources inform design choices; they do not establish the effectiveness of this coursework app. This is a focused literature scan, not a systematic review. Design implications below are project interpretations unless explicitly described as a study result.

## 1. Nonverbal self report and the emotion graph

Betella, A., and Verschure, P. F. M. J. (2016). *The Affective Slider: A Digital Self-Assessment Scale for the Measurement of Human Emotions*. PLOS ONE, 11(2), e0148037. [Original article](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0148037). DOI: 10.1371/journal.pone.0148037.

The authors compared two pleasure/arousal sliders with the Self-Assessment Manikin using emotional image ratings; 309 participants remained after exclusions. The measures correlated strongly at the image-rating level. This provides precedent for brief dimensional self-report. Our combined graph, five-position feeling slider, required color, and personal history are a different interface and have not inherited that validation. It is not a validated substitute for STAI or an objective anxiety measure. The original sliders used a neutral palette to avoid color-related bias; keep graph axes neutral and color selection separate. [Study methods and results](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0148037).

**Application:** label axes pleasantness and energy, provide an understandable point summary and a non-drag alternative. Assess whether requiring both a feeling slider and a graph creates duplicate effort. Nonverbal reporting can reduce writing demands; it does not eliminate social desirability bias.

## 2. Color as a personal expression channel

Jonauskaite, D., et al. (2020). *Universal Patterns in Color-Emotion Associations Are Further Shaped by Linguistic and Geographic Proximity*. Psychological Science, 31(10). DOI: 10.1177/0956797620948810. [Journal abstract](https://www.psychologicalscience.org/journals/psychological-science/0956797620948810/).

Across 4,598 participants in 30 nations, the study found shared color-emotion patterns alongside differences associated with nation, language, and geography. It does not validate reading an individual's mood from a color. Our design implication is to let the user define color meaning, keep an optional personal label, and avoid rules such as blue always meaning sadness. A color without a user-supplied meaning remains an uninterpreted preference, including when passed to a model.

## 3. Breathing as an interaction worth prototyping

Balban, M. Y., et al. (2023). *Brief structured respiration practices enhance mood and reduce physiological arousal*. Cell Reports Medicine, 4(1), 100895. DOI: 10.1016/j.xcrm.2022.100895. [PubMed abstract](https://pubmed.ncbi.nlm.nih.gov/36630953/).

This remote randomized study compared daily five-minute breathing practices with mindfulness meditation over one month. Exhale-focused cyclic sighing showed benefits for mood and respiratory rate. The practices and duration differ from this assignment's four-in/six-out, one-minute sequence. The paper supports investigating breathing interfaces, not a claim that our exact one-minute pattern produces those results. Use the assignment as the source for the fixed 4–6 steps and duration. Headspace and Apple Watch are user-named visual inspirations, not evidence for this prototype's outcomes.

## 4. A precedent for conversational CBT content

Fitzpatrick, K. K., Darcy, A., and Vierhile, M. (2017). *Delivering Cognitive Behavior Therapy to Young Adults With Symptoms of Depression and Anxiety Using a Fully Automated Conversational Agent (Woebot): A Randomized Controlled Trial*. JMIR Mental Health, 4(2), e19. DOI: 10.2196/mental.7785. [Original article](https://mental.jmir.org/2017/2/e19/).

Seventy young adults were randomized to two weeks of conversational CBT content or an information-only control. The study found a between-group depression benefit; it did not find a significant between-group anxiety benefit. This is a small, short, unblinded trial of a different system, not evidence for unrestricted LLM chat or a therapist replacement. It supports exploring conversational delivery and usability. Our open-ended chat still needs curated context, bounded behavior, failure handling, and separate safety access.

## 5. Concrete CBT source material

The Western Australia Centre for Clinical Interventions provides [anxiety resources](https://www.cci.health.wa.gov.au/Resources/For-Clinicians/Anxiety), including [Thought Diary 3](https://www.cci.health.wa.gov.au/~/media/CCI/Mental-Health-Professionals/Depression/Depression-Worksheets/Depression-Worksheet---08---Thought-Diary-3.pdf). The worksheet distinguishes situations, thoughts, feelings, evidence, and a balanced thought.

**Application:** use the assignment's simpler, fixed reframe sequence if a guided reframe is added. CCI is a candidate source for reviewed background and original fictional examples; do not reproduce an entire worksheet in the app or treat freely accessible material as permission for unrestricted redistribution. Source selection, licensing, version, scope, and an expected fictional response should be recorded before ingestion. Do not make users fill a full worksheet just to chat.

## 6. Intrusive thoughts and reassurance loops

CCI's [Reducing Reassurance Seeking](https://www.cci.health.wa.gov.au/~/media/CCI/Mental-Health-Professionals/Anxiety/Anxiety---Information-Sheets/Anxiety-Information-Sheet---20---Reducing-Reassurance-Seeking.pdf) describes how repeated reassurance can maintain anxiety despite providing temporary relief.

**Application:** the imagined audience includes intrusive thoughts, so repeated demands for certainty are an important fictional evaluation case. Do not equate intrusive thoughts with intent, diagnose OCD, promise certainty, or argue persistently until the person accepts a reframe. Record an unresolved content-policy decision for these situations before live-model implementation. This official information sheet informs that question; it does not establish an effective chatbot protocol.

## 7. What the fourteen Sleight of Mouth patterns are

The specific user interest is *Sleight of Mouth*, not generic natural language processing. [Robert Dilts's publication list](https://www.nlpu.com/NLPU_RBDPubs.html) identifies *Sleight of Mouth: The Magic of Conversational Belief Change* (1999). [Doug O'Brien's author site](https://www.sleightofmouth.org/) describes *The User's Guide to Sleight of Mouth* and says Dilts systematized patterns modeled from Richard Bandler's responses.

O'Brien's public list names Reality Strategy, Model of the World, Counter Example, Intent, Redefine, Chunking Up, Chunking Down, Metaphor or Analogy, Another Outcome, Consequence, Hierarchy of Criteria, Apply to Self, Changing Frame Size, and Meta Frame. These are author-described persuasion/reframing patterns, not fourteen clinically validated treatments. The full books were not reviewed; their text and examples have not been copied into this repository.

**Application:** preserve this as a proposed influence for the chat, not a silently discarded idea or an approved therapeutic method. Before using patterns, define a reviewed subset and original fictional examples. R3/R4 require respecting refusal: do not optimize for winning an argument, overcoming objections, or changing a person's beliefs without permission. A response-style setting cannot authorize coercive phrasing.

## 8. Evidence limits for neuro linguistic programming

Sturt, J., et al. (2012). *Neurolinguistic programming: a systematic review of the effects on health outcomes*. British Journal of General Practice, 62(604), e757–e764. DOI: 10.3399/bjgp12X658287. [Review abstract](https://pubmed.ncbi.nlm.nih.gov/23211179/).

The review included ten experimental studies and found little supporting evidence, with high or uncertain risk of bias. It interprets this as limited quantity and quality of evidence, not robust proof of no effect. It also did not isolate and test this app's fourteen-pattern implementation. Therefore CBT evidence cannot be used as evidence for Sleight of Mouth. No directly applicable trial of those fourteen patterns in this proposed app was established in this scan. Keep any use exploratory, clearly bounded, and subordinate to the assignment's fixed steps and user control.

## 9. RAG as context retrieval

Lewis, P., et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. NeurIPS 2020. [Original paper abstract](https://arxiv.org/abs/2005.11401).

The paper evaluates combining retrieval with generation on knowledge-intensive tasks. It provides a technical foundation for supplying relevant source passages. Those benchmarks do not establish clinical safety. In this project, retrieved material should have source identifiers and versions and remain separate from user history. Retrieval is not the same as clinically training a model. Begin with a small, curated corpus; a separate vector database is not yet justified. Review passages and generated outputs rather than assuming retrieval guarantees correctness.

## 10. Why a prompt alone is insufficient

Moore, J., et al. (2025). *Expressing stigma and inappropriate responses prevents LLMs from safely replacing mental health providers*. ACM FAccT 2025. DOI: 10.1145/3715275.3732039. [Author paper](https://arxiv.org/abs/2504.18412).

The authors evaluated model responses and reported stigma and inappropriate responses in mental-health situations. This evaluates particular models and scenarios, rather than proving every model behaves identically. It supports testing challenging fictional cases and limiting model authority. Exit controls, fixed skill state, persistence, and Help must be application behavior. Calm wording, curated RAG passages, and a system prompt do not establish safety or justify a therapist-replacement claim.

CCI's [Artificial Intelligence and Your Mental Health](https://www.cci.health.wa.gov.au/~/media/CCI/Mental-Health-Professionals/Generic-Resources/AI-and-Your-Mental-Health.pdf) is an additional official resource for reviewing the chat's role and communicating its limits before implementation.

## 11. Accessibility resources

W3C explains [use of color, SC 1.4.1](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html), [dragging alternatives, SC 2.5.7](https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements.html), and [animation from interactions, SC 2.3.3](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html). These support text labels and markers alongside calendar colors, tap/keyboard alternatives for graph placement, and reduced-motion behavior. SC 2.3.3 is Level AAA; these notes do not claim WCAG conformance. The wireframe and final app still need direct accessibility checks.

## 12. U.S. Help resources

The local-hotline lookup returned the [988 Suicide & Crisis Lifeline](https://988lifeline.org?oai_link_source=model_response_hotline), including [988](tel:988?oai_link_source=model_response_hotline) for crisis counseling. The [National 911 Program FAQ](https://www.911.gov/calling-911/frequently-asked-questions/) identifies 911 as the emergency-services route. The user confirmed United States coverage. Label these separately and keep the prototype's call actions simulated. Do not describe either as in-app therapy or an app-operated service.

## Research conclusions and remaining questions

The strongest fit is brief dimensional self-report, a simple breathing cue, and carefully sourced conversational content. The evidence does not validate the combined interface, infer emotions from colors, establish superiority to STAI, validate fourteen NLP patterns, or justify deployment to people in distress.

Before implementation, resolve the feeling-slider labels, burden of three required logging inputs, history-context consent, provider/data transmission, approved corpus and rights, reply-setting values, and crisis/reassurance response policies. Adaptive UI remains open. Mouse-click and eye-tracking papers mentioned in the earlier discussion were not supplied or used as evidence; passive sensing remains deferred.

## Subsequent chat communication research on October 26 2026

The user requested extensive web research on leading mental health chatbots,
spoken/written communication, therapist training, suicide-related language, and
edge cases to inform a future system-prompt revision. The user clarified that
research should cover adults and teenagers and dynamic adaptation. The
[communication research brief](chatbot-communication-research.md) compares seven
systems, distinguishes product claims from study findings, translates professional
communication guidance into bounded proposals, and includes an unapplied prompt
draft plus 24 fictional evaluation scenarios. All scenario results remain not run.

The proposed adaptation uses stated age, preferences, and supplied context;
eligibility, any age input, and UI adaptation remain separate decisions. The
research does not change application prompts or establish suitability for minors.
The Part 3.1 findings above remain historical. Source access, acoustic verification,
and clinical evidence limits are recorded in the new brief.
