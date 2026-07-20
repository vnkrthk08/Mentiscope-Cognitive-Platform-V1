import { Question } from "../types";

export const QUESTIONS_DATA: { [moduleId: string]: Question[] } = {
  gq: [
    {
      id: "gq-1",
      text: "Which of the figures should logically complete the pattern?",
      story: "Logical Sequence: You are presented with a grid pattern. Each row follows a rule: circles increase in size, triangles rotate 90 degrees clockwise.",
      options: ["Large Circle with rotated triangle", "Medium Circle with normal triangle", "Small Square with rotated triangle", "None of the above"],
      correctAnswer: "Large Circle with rotated triangle",
      hint: "Rotate the triangle 90 degrees and look at the progression of circle sizes.",
      type: "choice"
    },
    {
      id: "gq-2",
      text: "All prompt-readers are learners. Some learners are coders. Therefore, some prompt-readers are coders.",
      story: "Syllogistic Reasoning: Determine if the conclusion logically follows from the premises.",
      options: ["Definitely True", "Definitely False", "Cannot be determined from the premises", "None of the above"],
      correctAnswer: "Cannot be determined from the premises",
      hint: "Being a learner is the link. But prompt-readers and coders might be separate sets of learners.",
      type: "choice"
    },
    {
      id: "gq-3",
      text: "If 5 machines take 5 minutes to make 5 widgets, how long would it take 100 machines to make 100 widgets?",
      story: "System Rate Problem: Calculate the time needed for scaling operations.",
      options: ["100 minutes", "50 minutes", "5 minutes", "25 minutes"],
      correctAnswer: "5 minutes",
      hint: "Each machine takes 5 minutes to make 1 widget.",
      type: "choice"
    },
    {
      id: "gq-4",
      text: "A clock shows 3:15. What is the angle between the hour hand and the minute hand?",
      story: "Spatial & Analog Tracking: Calculate exact rotational differences.",
      options: ["0 degrees", "7.5 degrees", "15 degrees", "22.5 degrees"],
      correctAnswer: "7.5 degrees",
      hint: "Remember that the hour hand moves slightly as the minute hand moves to 15 minutes.",
      type: "choice"
    },
    {
      id: "gq-5",
      text: "Which word does not belong with the others?",
      story: "Category Exclusion: Select the semantic outlier.",
      options: ["Ocular", "Olfactory", "Tactile", "Cognitive"],
      correctAnswer: "Cognitive",
      hint: "Three of these correspond directly to primary sensory organs, while one is a central mental process.",
      type: "choice"
    }
  ],
  gsm: [
    {
      id: "gsm-1",
      text: "Repeat the sequence in the correct order.",
      story: "Working Memory (Digit Span Forward): Listen or watch carefully. Remember this sequence of digits.",
      sequence: [4, 8, 2, 9, 1],
      type: "memory-span",
      correctAnswer: "48291",
      hint: "Type the numbers exactly as they appeared: Four, Eight, Two, Nine, One."
    },
    {
      id: "gsm-2",
      text: "Repeat the sequence in REVERSE order.",
      story: "Working Memory (Digit Span Backward): Reverse processing forces active storage manipulation.",
      sequence: [3, 7, 5, 1, 8],
      type: "memory-span",
      correctAnswer: "81573",
      hint: "Take the sequence 3, 7, 5, 1, 8 and type it backwards."
    },
    {
      id: "gsm-3",
      text: "Remember and repeat this mixed alpha-numeric span in ascending order.",
      story: "Alpha-Numeric Span Sort: Sort numbers first, then letters in alphabetical order.",
      sequence: ["B", 5, "A", 2, "C", 8],
      type: "memory-span",
      correctAnswer: "258ABC",
      hint: "Order numbers first (2, 5, 8) then letters (A, B, C)."
    },
    {
      id: "gsm-4",
      text: "Look at the pattern grid. Which coordinates contained the highlighted cells?",
      story: "Visual-Spatial Working Memory: Remember active cells on a 4x4 matrix.",
      gridSize: 4,
      activeGridCells: [2, 7, 13],
      type: "grid-pattern",
      correctAnswer: "2,7,13",
      hint: "Remember the row/column indices (zero-indexed: top-left is 0, bottom-right is 15)."
    },
    {
      id: "gsm-5",
      text: "Enter the sum of the first digit and the last digit from this sequence: 7, 2, 9, 4, 3",
      story: "Active Arithmetic Memory: Hold the sequence while performing an arithmetic operation.",
      sequence: [7, 2, 9, 4, 3],
      options: ["9", "10", "11", "12"],
      correctAnswer: "10",
      hint: "Add the first digit (7) and the last digit (3)."
    }
  ],
  gf: [
    {
      id: "gf-1",
      text: "Find the missing piece that completes the 3x3 matrix logic.",
      story: "Raven's Progressive Matrix: Column-wise, shapes add together, overlapping lines disappear (XOR gate logic).",
      options: ["Cross within a circle", "Square within a triangle", "Plain Circle", "Double crossed lines"],
      correctAnswer: "Cross within a circle",
      hint: "Superimpose column 1 onto column 2 and cancel out identical strokes.",
      type: "choice"
    },
    {
      id: "gf-2",
      text: "Choose the pair that shares the identical logical relation as: CRUCIBLE : METAL",
      story: "Analogical Reasoning: Identify abstract structural relationships.",
      options: ["Oven : Bread", "Forest : Tree", "Envelope : Letter", "Acre : Land"],
      correctAnswer: "Oven : Bread",
      hint: "A crucible is a vessel used to refine and transform metal; an oven is a container used to bake and transform bread.",
      type: "choice"
    },
    {
      id: "gf-3",
      text: "A is the father of B. C is the daughter of B. D is the brother of C. What is the relation of A to D?",
      story: "Relational Mapping: Construct a structural kinship chart.",
      options: ["Grandfather", "Grandmother", "Father", "Uncle"],
      correctAnswer: "Grandfather",
      hint: "Since A is the father of B, and D is B's son, A is D's grandfather.",
      type: "choice"
    },
    {
      id: "gf-4",
      text: "Look at the sequence: 2, 6, 12, 20, 30. What is the next number?",
      story: "Numerical Induction: Infer the generative formula.",
      options: ["40", "42", "44", "46"],
      correctAnswer: "42",
      hint: "Look at the differences: +4, +6, +8, +10. The next difference should be +12.",
      type: "choice"
    },
    {
      id: "gf-5",
      text: "In a certain code, COGNITIVE is written as EQIPKVKXG. How is MENTISCOPE written?",
      story: "Inductive Rule Discovery: Deduce the shift cipher code.",
      options: ["OGPVKUEQRG", "OGPVISCORG", "NFOUJTDQPF", "PHOVKUEQRE"],
      correctAnswer: "OGPVKUEQRG",
      hint: "Each letter is shifted by +2 positions in the alphabet (C->E, O->Q, etc.).",
      type: "choice"
    }
  ],
  attention: [
    {
      id: "attn-1",
      text: "Select the actual font color of the word below, NOT what it says.",
      story: "Stroop Interference Test: Resolve the response conflict between read word and font color.",
      textColor: "RED",
      targetColor: "GREEN",
      options: ["RED", "GREEN", "BLUE", "YELLOW"],
      correctAnswer: "GREEN",
      hint: "The word says 'RED', but it is colored GREEN. Respond with the actual color you see.",
      type: "stroop"
    },
    {
      id: "attn-2",
      text: "Select the actual font color of the word below, NOT what it says.",
      story: "Stroop Interference Test: Overcome pre-potent reading impulse.",
      textColor: "BLUE",
      targetColor: "YELLOW",
      options: ["BLUE", "GREEN", "YELLOW", "RED"],
      correctAnswer: "YELLOW",
      hint: "Look at the visual paint color: it is yellow. Ignore the spelling.",
      type: "stroop"
    },
    {
      id: "attn-3",
      text: "Count the number of times the letter 'F' appears in the following sentence: 'FINISHED FILES ARE THE RESULT OF YEARS OF SCIENTIFIC STUDY'",
      story: "Visual Scanning & Selective Attention: Scanning strings for target phonemes/graphemes.",
      options: ["3", "4", "5", "6"],
      correctAnswer: "6",
      hint: "Read carefully and do not skip the 'OF' words! Most people miss the 'F' in 'OF' because we process them holistically.",
      type: "choice"
    },
    {
      id: "attn-4",
      text: "Select the correct match for the word printed in the Stroop test color.",
      story: "Stroop Matching Task: Choose the font color of the word: 'ORANGE' printed in BLUE.",
      textColor: "ORANGE",
      targetColor: "BLUE",
      options: ["ORANGE", "BLUE", "RED", "GREEN"],
      correctAnswer: "BLUE",
      hint: "The font color is BLUE. Ignore the semantic meaning 'ORANGE'.",
      type: "stroop"
    },
    {
      id: "attn-5",
      text: "Which of the following targets matches the arrow pointing direction? ← ← → ← ←",
      story: "Flanker Conflict Task: Respond only to the center arrow direction.",
      options: ["Left", "Right", "Up", "Down"],
      correctAnswer: "Right",
      hint: "Look strictly at the center (3rd) arrow: '→'. It points Right.",
      type: "choice"
    }
  ],
  language: [
    {
      id: "lang-1",
      text: "Find the synonym of: ERUDITE",
      story: "Lexical Knowledge: Identify sophisticated vocabulary matches.",
      options: ["Ignorant", "Scholarly", "Evasive", "Articulate"],
      correctAnswer: "Scholarly",
      hint: "An erudite person is someone who possesses deep knowledge and scholarship.",
      type: "choice"
    },
    {
      id: "lang-2",
      text: "Which analogy represents the relations of: EPHEMERAL : ETERNAL?",
      story: "Semantic Analogies: Contrast duration and longevity concepts.",
      options: ["Transient : Permanent", "Vast : Infinite", "Fragile : Delicate", "Swift : Immediate"],
      correctAnswer: "Transient : Permanent",
      hint: "Ephemeral means short-lived, while eternal means forever (antonyms). Transient and permanent are also antonyms.",
      type: "choice"
    },
    {
      id: "lang-3",
      text: "Complete the sentence: 'The scholar's arguments were so ______ that even his fiercest critics had to ______ his brilliance.'",
      story: "Sentence Completion & Contextual Logic: Deduce syntactic consistency and tone.",
      options: ["flawed ... dismiss", "cogent ... acknowledge", "convoluted ... applaud", "banal ... ignore"],
      correctAnswer: "cogent ... acknowledge",
      hint: "The second part says 'even his fiercest critics' had to agree, meaning his arguments were powerful (cogent) and they had to accept (acknowledge) them.",
      type: "choice"
    },
    {
      id: "lang-4",
      text: "Unscramble these letters to make a word: T M S Y O P M. What is it?",
      story: "Anagram & Phonology: Word reconstruction from mental phoneme bins.",
      options: ["SYMPTOM", "SYSTEM", "MYSTIC", "POSTMAN"],
      correctAnswer: "SYMPTOM",
      hint: "It starts with S and ends with M. Often represents a sign of condition.",
      type: "choice"
    },
    {
      id: "lang-5",
      text: "Which of these is the antonym of: ALACRITY?",
      story: "Vocabulary Contrasts: Deduce the opposite semantic state.",
      options: ["Eagerness", "Apathy", "Speed", "Agility"],
      correctAnswer: "Apathy",
      hint: "Alacrity means brisk, cheerful readiness. Its antonym is sluggish indifference or apathy.",
      type: "choice"
    }
  ],
  executive: [
    {
      id: "exec-1",
      text: "What is the minimum number of moves to transfer 3 disks from Peg A to Peg C in the Tower of Hanoi?",
      story: "Executive Planning & Working Sub-goals: Plan sequential movements following pegs rule.",
      options: ["3 moves", "5 moves", "7 moves", "9 moves"],
      correctAnswer: "7 moves",
      hint: "The formula is 2^n - 1, where n is the number of disks.",
      type: "choice"
    },
    {
      id: "exec-2",
      text: "If a card sorting rule switches from 'Color' to 'Shape', which card matches the Blue Triangle under the new rule?",
      story: "Cognitive Shifting: Wisconsin Card Sorting test adaptation logic.",
      options: ["Red Triangle", "Blue Circle", "Green Square", "Blue Star"],
      correctAnswer: "Red Triangle",
      hint: "The rule switched to SHAPE. Thus, color is irrelevant. The match must be a Triangle.",
      type: "choice"
    },
    {
      id: "exec-3",
      text: "You have a 3-liter jug and a 5-liter jug. How can you measure exactly 4 liters of water from an unlimited tap?",
      story: "Strategic Goal Management: Formulate multistep planning operations.",
      options: [
        "Fill 5L, pour into 3L (leaving 2L). Empty 3L, pour 2L into 3L. Fill 5L and pour into 3L until full (pouring 1L, leaving 4L).",
        "Fill 3L, pour into 5L twice to overflow.",
        "Fill both jugs and take the average.",
        "This is mathematically impossible."
      ],
      correctAnswer: "Fill 5L, pour into 3L (leaving 2L). Empty 3L, pour 2L into 3L. Fill 5L and pour into 3L until full (pouring 1L, leaving 4L).",
      hint: "Follow the steps of filling, pouring, and subtracting capacities to isolate 4 liters.",
      type: "choice"
    },
    {
      id: "exec-4",
      text: "In a schedule, task B can only start after A is completed. C can start after A but must finish before D starts. If D starts on Tuesday, when is the earliest C can finish?",
      story: "Task Prioritization & Scheduling Constraints: Resolve dependency trees.",
      options: ["Monday", "Tuesday", "Wednesday", "Cannot be determined"],
      correctAnswer: "Monday",
      hint: "Since C must finish before D starts, and D starts on Tuesday, C must finish on or before Monday.",
      type: "choice"
    },
    {
      id: "exec-5",
      text: "Which action is the most critical first step if a primary test server starts returning 500 Server Errors?",
      story: "Emergency Triaging: Cognitive decision hierarchy.",
      options: [
        "Check system logs to isolate the error root cause",
        "Reboot the entire hosting infrastructure",
        "Notify all users and apologize immediately",
        "Rewrite the database handler from scratch"
      ],
      correctAnswer: "Check system logs to isolate the error root cause",
      hint: "Diagnostic visibility (logs) must precede destructive action (rebooting) or corrective work.",
      type: "choice"
    }
  ]
};
