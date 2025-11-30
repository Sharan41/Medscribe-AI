# BMAD Agent Usage Guide - MedScribe Project

**Quick Reference:** How to activate and work with each BMAD agent for the Medical Scribe project.

---

## 🎯 How to Activate Agents

### Method 1: Direct Agent Reference
Use `@bmad/bmm/agents/{agent-name}` in your chat to activate an agent.

**Example:**
```
@bmad/bmm/agents/pm I need help creating a PRD for the medical scribe app.
```

### Method 2: Workflow Activation
Agents are automatically activated when you use their workflows.

**Example:**
```
@bmad/bmm/workflows/prd Let's create the PRD for MedScribe.
```

---

## 👥 Agent Activation Guide

### 1. Analyst 🔍 - Domain Research

**Activation:**
```
@bmad/bmm/agents/analyst
```

**When to Use:**
- Starting Phase 1 research
- Need competitive analysis
- Technology stack decisions
- Regulatory compliance questions

**Example Commands:**
```
@bmad/bmm/agents/analyst Research Indian healthcare regulations for medical records.
@bmad/bmm/workflows/domain-research Analyze speech-to-text APIs for Indian languages.
```

**Key Workflows:**
- `domain-research` - Comprehensive domain analysis
- `research` - General research tasks

---

### 2. PM (Product Manager) 📋 - Requirements & Planning

**Activation:**
```
@bmad/bmm/agents/pm
```

**When to Use:**
- Creating product brief
- Writing PRD
- Breaking down epics
- Prioritizing features
- Validating requirements

**Example Commands:**
```
@bmad/bmm/agents/pm Create a product brief for MedScribe AI.
@bmad/bmm/workflows/product-brief Let's define the product vision.
@bmad/bmm/workflows/prd Create the PRD with all features.
@bmad/bmm/workflows/create-epics-and-stories Break down the PRD into epics and stories.
```

**Key Workflows:**
- `product-brief` - Product vision document
- `prd` - Product Requirements Document
- `create-epics-and-stories` - Epic and story breakdown
- `tech-spec` - Technical specifications (for simple features)

---

### 3. UX Designer 🎨 - User Experience Design

**Activation:**
```
@bmad/bmm/agents/ux-designer
```

**When to Use:**
- Designing user interface
- Creating wireframes
- User journey mapping
- Accessibility requirements
- Mobile-first design

**Example Commands:**
```
@bmad/bmm/agents/ux-designer Design the consultation recording interface.
@bmad/bmm/workflows/create-ux-design Create wireframes for the doctor's dashboard.
@bmad/bmm/workflows/create-excalidraw-wireframe Create wireframe for the recording screen.
```

**Key Workflows:**
- `create-ux-design` - Complete UX design process
- `create-excalidraw-wireframe` - Interactive wireframes
- `create-excalidraw-diagram` - User flow diagrams

---

### 4. Architect 🏛️ - System Architecture

**Activation:**
```
@bmad/bmm/agents/architect
```

**When to Use:**
- Designing system architecture
- API design
- Database schema design
- Security architecture
- Integration design
- Technology decisions

**Example Commands:**
```
@bmad/bmm/agents/architect Design the system architecture for MedScribe.
@bmad/bmm/workflows/architecture Create the complete system architecture.
@bmad/bmm/workflows/create-excalidraw-dataflow Design the data flow diagram.
@bmad/bmm/workflows/implementation-readiness Check if we're ready to start coding.
```

**Key Workflows:**
- `architecture` - Complete system architecture
- `implementation-readiness` - Pre-implementation checklist
- `create-excalidraw-dataflow` - Data flow diagrams
- `create-excalidraw-diagram` - Architecture diagrams

---

### 5. SM (Scrum Master) 🎯 - Sprint Planning

**Activation:**
```
@bmad/bmm/agents/sm
```

**When to Use:**
- Sprint planning
- Story refinement
- Progress tracking
- Removing blockers
- Story management

**Example Commands:**
```
@bmad/bmm/agents/sm Plan Sprint 1 for MedScribe.
@bmad/bmm/workflows/sprint-planning Create sprint plan for weeks 5-6.
@bmad/bmm/workflows/story-ready Make stories ready for development.
@bmad/bmm/workflows/story-context Provide context for story MED-123.
```

**Key Workflows:**
- `sprint-planning` - Sprint planning session
- `story-ready` - Prepare stories for development
- `story-context` - Add technical context to stories
- `workflow-status` - Check project status

---

### 6. DEV (Developer) 💻 - Implementation

**Activation:**
```
@bmad/bmm/agents/dev
```

**When to Use:**
- Writing code
- Implementing features
- Code reviews
- Bug fixes
- Technical implementation questions

**Example Commands:**
```
@bmad/bmm/agents/dev Implement the audio recording feature.
@bmad/bmm/workflows/dev-story Implement story MED-123.
@bmad/bmm/workflows/code-review Review the transcription API code.
@bmad/bmm/workflows/story-done Mark story MED-123 as done.
```

**Key Workflows:**
- `dev-story` - Implement a user story
- `code-review` - Code review process
- `story-done` - Complete story workflow
- `correct-course` - Fix implementation issues

---

### 7. TEA (Test Architect) 🧪 - Quality Assurance

**Activation:**
```
@bmad/bmm/agents/tea
```

**When to Use:**
- Test strategy
- Writing tests
- Quality assurance
- Performance testing
- Security testing

**Example Commands:**
```
@bmad/bmm/agents/tea Create test strategy for MedScribe.
@bmad/bmm/workflows/framework Set up testing framework.
@bmad/bmm/workflows/atdd Create acceptance tests for transcription feature.
@bmad/bmm/workflows/automate Automate tests for the API.
```

**Key Workflows:**
- `framework` - Set up testing framework
- `atdd` - Acceptance Test-Driven Development
- `automate` - Test automation
- `trace` - Test traceability
- `ci` - CI/CD integration

---

### 8. Technical Writer 📚 - Documentation

**Activation:**
```
@bmad/bmm/agents/tech-writer
```

**When to Use:**
- API documentation
- User guides
- Architecture documentation
- Deployment guides
- Project documentation

**Example Commands:**
```
@bmad/bmm/agents/tech-writer Document the transcription API.
@bmad/bmm/workflows/document-project Create project documentation.
```

**Key Workflows:**
- `document-project` - Complete project documentation

---

## 🔄 Typical Workflow Sequence

### Phase 1: Analysis
```
1. @bmad/bmm/workflows/domain-research
   → Analyst researches domain

2. @bmad/bmm/workflows/product-brief
   → PM creates product brief
```

### Phase 2: Planning
```
3. @bmad/bmm/workflows/prd
   → PM creates PRD

4. @bmad/bmm/workflows/create-ux-design
   → UX Designer creates designs

5. @bmad/bmm/workflows/architecture
   → Architect designs system
```

### Phase 3: Solutioning
```
6. @bmad/bmm/workflows/implementation-readiness
   → Architect ensures readiness
```

### Phase 4: Implementation
```
7. @bmad/bmm/workflows/sprint-planning
   → SM plans sprint

8. @bmad/bmm/workflows/story-ready
   → SM prepares stories

9. @bmad/bmm/workflows/dev-story
   → DEV implements story

10. @bmad/bmm/workflows/story-done
    → DEV completes story

11. @bmad/bmm/workflows/code-review
    → DEV reviews code
```

---

## 🎪 Party Mode - Multi-Agent Collaboration

**When to Use:**
- Complex decisions requiring multiple perspectives
- Brainstorming sessions
- Retrospectives
- Sprint planning discussions

**Activation:**
```
@bmad/core/workflows/party-mode
```

**Example:**
```
@bmad/core/workflows/party-mode 
Topic: Should we use Reverie API or fine-tune Whisper first?
Include: PM, Architect, Analyst
```

**Agents Available:**
- PM, Analyst, Architect, SM, DEV, TEA, UX Designer, Technical Writer

---

## 📋 Quick Command Reference

### Starting the Project
```bash
# Initialize BMAD (if not done)
# Then start with:

@bmad/bmm/workflows/domain-research
```

### Creating PRD
```bash
@bmad/bmm/workflows/prd
```

### Designing Architecture
```bash
@bmad/bmm/workflows/architecture
```

### Starting Development
```bash
@bmad/bmm/workflows/sprint-planning
@bmad/bmm/workflows/dev-story
```

### Checking Status
```bash
@bmad/bmm/workflows/workflow-status
```

---

## 💡 Tips

1. **One Agent at a Time:** Usually work with one agent per task
2. **Use Workflows:** Workflows guide you through complete processes
3. **Party Mode for Complex Decisions:** When you need multiple perspectives
4. **Check Status Regularly:** Use `workflow-status` to track progress
5. **Document as You Go:** Technical Writer can help document decisions

---

## 🆘 Getting Help

- **BMAD Master:** Use `@bmad/core/agents/bmad-master` for orchestration help
- **Workflow Status:** Use `@bmad/bmm/workflows/workflow-status` to see where you are
- **Documentation:** Check `.cursor/rules/bmad/bmm/docs/` for detailed guides

---

**Last Updated:** {{current_date}}

