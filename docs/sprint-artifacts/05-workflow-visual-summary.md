# MedScribe AI - BMAD Workflow Visual Summary

**Visual representation of the BMAD methodology workflow for MedScribe AI project.**

---

## 📊 Overall Project Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 0: INITIALIZATION                      │
│                    (Week 1)                                     │
│  • Set up project structure                                     │
│  • Initialize Git                                               │
│  • Set up development environment                               │
│  • Create BMAD configuration                                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              PHASE 1: ANALYSIS & RESEARCH                        │
│              (Weeks 1-2)                                         │
│                                                                  │
│  ┌──────────────────┐         ┌──────────────────┐             │
│  │  Analyst Agent   │────────▶│   PM Agent       │             │
│  │  🔍              │         │   📋              │             │
│  │                  │         │                  │             │
│  │ • Domain Research│         │ • Product Brief  │             │
│  │ • Tech Research  │         │ • Vision         │             │
│  │ • Competitive    │         │ • Goals          │             │
│  │   Analysis       │         │                  │             │
│  └──────────────────┘         └──────────────────┘             │
│                                                                  │
│  Deliverables:                                                  │
│  • Domain Research Document                                     │
│  • Product Brief                                                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 2: PLANNING                             │
│                    (Weeks 2-4)                                   │
│                                                                  │
│  ┌──────────────────┐         ┌──────────────────┐             │
│  │   PM Agent       │         │  UX Designer     │             │
│  │   📋             │         │   🎨             │             │
│  │                  │         │                  │             │
│  │ • PRD            │         │ • Wireframes     │             │
│  │ • Epics          │         │ • Mockups        │             │
│  │ • User Stories   │         │ • Design System  │             │
│  └──────────────────┘         └──────────────────┘             │
│                                                                  │
│  Deliverables:                                                  │
│  • Product Requirements Document (PRD)                          │
│  • Epic Breakdown                                               │
│  • User Stories                                                 │
│  • UX Designs & Wireframes                                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   PHASE 3: SOLUTIONING                           │
│                   (Weeks 4-5)                                    │
│                                                                  │
│  ┌──────────────────┐         ┌──────────────────┐             │
│  │  Architect       │────────▶│  Architect       │             │
│  │   🏛️            │         │   🏛️            │             │
│  │                  │         │                  │             │
│  │ • Architecture   │         │ • Implementation │             │
│  │ • API Design     │         │   Readiness      │             │
│  │ • Database       │         │ • Checklist      │             │
│  │ • Security       │         │                  │             │
│  └──────────────────┘         └──────────────────┘             │
│                                                                  │
│  Deliverables:                                                  │
│  • System Architecture Diagram                                  │
│  • API Specifications                                           │
│  • Database Schema                                              │
│  • Security Architecture                                        │
│  • Implementation Readiness Checklist                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  PHASE 4: IMPLEMENTATION                         │
│                  (Weeks 5-12)                                    │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ SM Agent     │  │ DEV Agent    │  │ TEA Agent    │         │
│  │  🎯          │  │  💻          │  │  🧪          │         │
│  │              │  │              │  │              │         │
│  │ • Sprint     │─▶│ • Code       │─▶│ • Tests      │         │
│  │   Planning   │  │ • Features   │  │ • QA         │         │
│  │ • Stories    │  │ • Reviews    │  │ • Automation │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
│  Sprint 1: Foundation (Weeks 5-6)                               │
│  Sprint 2: Audio Recording (Weeks 6-7)                          │
│  Sprint 3: Speech-to-Text (Weeks 7-9)                           │
│  Sprint 4: Note Generation (Weeks 9-10)                         │
│  Sprint 5: Polish & Security (Weeks 10-11)                      │
│  Sprint 6: Testing & Deployment (Weeks 11-12)                    │
│                                                                  │
│  Deliverables:                                                  │
│  • Working application                                          │
│  • Test suite                                                   │
│  • Documentation                                                │
│  • Deployed production system                                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Agent Workflow Sequence

### Phase 1: Analysis
```
Analyst 🔍
  │
  ├─ domain-research workflow
  │   └─> Domain Research Document
  │
  └─> PM 📋
      │
      └─ product-brief workflow
          └─> Product Brief
```

### Phase 2: Planning
```
PM 📋
  │
  ├─ prd workflow
  │   └─> PRD Document
  │
  └─ create-epics-and-stories workflow
      └─> Epics & User Stories
          │
          └─> UX Designer 🎨
              │
              └─ create-ux-design workflow
                  └─> Wireframes & Mockups
```

### Phase 3: Solutioning
```
Architect 🏛️
  │
  ├─ architecture workflow
  │   ├─> System Architecture
  │   ├─> API Specifications
  │   ├─> Database Schema
  │   └─> Security Architecture
  │
  └─ implementation-readiness workflow
      └─> Implementation Readiness Checklist
```

### Phase 4: Implementation (Iterative)
```
SM 🎯
  │
  └─ sprint-planning workflow
      └─> Sprint Plan
          │
          ├─> DEV 💻
          │   │
          │   ├─ dev-story workflow
          │   │   └─> Implemented Feature
          │   │
          │   └─ code-review workflow
          │       └─> Reviewed Code
          │
          └─> TEA 🧪
              │
              ├─ framework workflow
              │   └─> Test Framework
              │
              ├─ atdd workflow
              │   └─> Acceptance Tests
              │
              └─ automate workflow
                  └─> Automated Tests
```

---

## 🎯 Feature Development Flow

### Example: Audio Recording Feature

```
1. SM 🎯: Sprint Planning
   └─> Story: "As a doctor, I want to record consultations"
   
2. SM 🎯: Story Ready
   └─> Add technical context, acceptance criteria
   
3. DEV 💻: Dev Story
   ├─> Backend: Audio upload endpoint
   ├─> Frontend: Recording UI
   └─> Integration: Connect frontend to backend
   
4. DEV 💻: Code Review
   └─> Review code quality, best practices
   
5. TEA 🧪: Write Tests
   ├─> Unit tests
   ├─> Integration tests
   └─> E2E tests
   
6. DEV 💻: Story Done
   └─> Feature complete, tested, documented
```

---

## 🔀 Parallel Workflows

### During Implementation Phase:

```
┌─────────────────────────────────────────────────────────┐
│              Parallel Development Streams                │
│                                                          │
│  Stream 1: Core Features          Stream 2: Testing     │
│  ┌──────────────┐                ┌──────────────┐      │
│  │ DEV 💻       │                │ TEA 🧪       │      │
│  │              │                │              │      │
│  │ • Features   │                │ • Test       │      │
│  │ • Code       │                │   Strategy   │      │
│  │ • Reviews    │                │ • Automation │      │
│  └──────────────┘                └──────────────┘      │
│                                                          │
│  Stream 3: Documentation         Stream 4: DevOps       │
│  ┌──────────────┐                ┌──────────────┐      │
│  │ Tech Writer  │                │ DEV 💻       │      │
│  │ 📚           │                │              │      │
│  │ • API Docs   │                │ • CI/CD      │      │
│  │ • User Guide │                │ • Deployment │      │
│  └──────────────┘                └──────────────┘      │
└─────────────────────────────────────────────────────────┘
```

---

## 🎪 Party Mode Usage

### When to Use Multi-Agent Collaboration:

```
Complex Decision Point
  │
  └─> Party Mode 🎪
      │
      ├─> PM 📋: Product perspective
      ├─> Architect 🏛️: Technical perspective
      ├─> Analyst 🔍: Research perspective
      └─> UX Designer 🎨: User perspective
          │
          └─> Consensus Decision
```

**Example Topics:**
- "Should we use Reverie API or fine-tune Whisper first?"
- "What's the best architecture for offline support?"
- "How should we prioritize Phase 2 features?"

---

## 📈 Progress Tracking

### Workflow Status Flow:

```
Regular Check-ins
  │
  └─> workflow-status workflow
      │
      ├─> Current Phase
      ├─> Completed Workflows
      ├─> In-Progress Workflows
      ├─> Blockers
      └─> Next Steps
```

**Use weekly:** `@bmad/bmm/workflows/workflow-status`

---

## 🔄 Iterative Improvement

### Retrospective Flow:

```
End of Sprint/Epic
  │
  └─> retrospective workflow
      │
      ├─> What went well?
      ├─> What could improve?
      ├─> Action items
      └─> Update process
          │
          └─> Apply to next sprint
```

---

## 🎯 Decision Points

### Key Decision Gates:

```
Phase Completion Gate
  │
  ├─> All deliverables complete?
  │   ├─ YES → Proceed to next phase
  │   └─ NO → Complete missing items
  │
  └─> Quality check passed?
      ├─ YES → Proceed
      └─ NO → Fix issues
```

**Gates:**
1. Phase 1 → Phase 2: Research complete, product brief approved
2. Phase 2 → Phase 3: PRD complete, UX designs approved
3. Phase 3 → Phase 4: Architecture complete, implementation ready
4. Phase 4 → Launch: All sprints complete, tested, deployed

---

## 📚 Documentation Flow

```
Throughout Project
  │
  └─> Technical Writer 📚
      │
      ├─> Document decisions
      ├─> API documentation
      ├─> User guides
      └─> Deployment guides
```

**Documentation happens continuously, not just at the end!**

---

## 🚀 Quick Reference: Agent → Workflow Mapping

| Agent | Primary Workflows | When to Use |
|-------|------------------|-------------|
| **Analyst** 🔍 | `domain-research`, `research` | Phase 1: Research |
| **PM** 📋 | `product-brief`, `prd`, `create-epics-and-stories` | Phase 2: Planning |
| **UX Designer** 🎨 | `create-ux-design`, `create-excalidraw-wireframe` | Phase 2: Design |
| **Architect** 🏛️ | `architecture`, `implementation-readiness` | Phase 3: Solutioning |
| **SM** 🎯 | `sprint-planning`, `story-ready`, `story-context` | Phase 4: Sprint management |
| **DEV** 💻 | `dev-story`, `code-review`, `story-done` | Phase 4: Implementation |
| **TEA** 🧪 | `framework`, `atdd`, `automate` | Phase 4: Testing |
| **Tech Writer** 📚 | `document-project` | All phases: Documentation |

---

**Last Updated:** {{current_date}}

