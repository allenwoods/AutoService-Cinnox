# Review Dimensions by Document Type

Each document type has a set of evaluation dimensions. Use these as a guide — reviewers may skip, reorder, or add dimensions as needed.

---

## Plan (Architecture / Design)

For documents in `docs/plans/` describing system architecture, technical design, or migration plans.

### Dimensions

1. **Problem Definition**
   - Is the problem clearly stated with concrete evidence?
   - Are the pain points real and significant?
   - Is the scope well-bounded (goals vs. non-goals)?

2. **Solution Design**
   - Does the proposed solution address all stated problems?
   - Is the architecture clear and internally consistent?
   - Are component responsibilities well-defined?
   - Are interfaces between components explicit?

3. **Alternatives Analysis**
   - Were viable alternatives considered?
   - Is the comparison fair and thorough?
   - Is the rationale for the chosen approach convincing?
   - Are there unconsidered alternatives?

4. **Feasibility & Complexity**
   - Is the solution technically feasible with current resources?
   - Is the complexity proportional to the problem?
   - Are there simpler approaches that would suffice?
   - Are dependencies and prerequisites identified?

5. **Risk Assessment**
   - Are risks identified comprehensively?
   - Are mitigation strategies concrete and actionable?
   - Are there unidentified risks?
   - What's the worst-case scenario?

6. **Migration & Rollout**
   - Is the migration path clear and phased?
   - Are rollback strategies defined?
   - Is the timeline realistic?
   - What are the dependencies between phases?

7. **Maintainability**
   - Will this design be easy to understand for new team members?
   - Are operational concerns addressed (monitoring, debugging)?
   - Does it create tech debt? Is that debt acknowledged?

---

## PRD (Product Requirements)

For product requirement documents describing features, user stories, and acceptance criteria.

### Dimensions

1. **User Problem**
   - Is the user problem clearly articulated?
   - Is there evidence of real user need (data, feedback, research)?
   - Who are the target users? Are personas defined?

2. **Requirements Completeness**
   - Are functional requirements specific and testable?
   - Are non-functional requirements defined (performance, security, accessibility)?
   - Are edge cases and error states covered?
   - Are acceptance criteria measurable?

3. **Scope & Priority**
   - Is the scope well-defined (in-scope vs. out-of-scope)?
   - Are requirements prioritized (must-have vs. nice-to-have)?
   - Is the MVP clearly identified?

4. **User Experience**
   - Are user flows described?
   - Are interaction patterns clear?
   - Is the design consistent with existing product patterns?
   - Are accessibility concerns addressed?

5. **Technical Feasibility**
   - Are there known technical constraints?
   - Are integration points identified?
   - Are data requirements specified?

6. **Success Metrics**
   - How will success be measured?
   - Are metrics specific and time-bound?
   - Is there a baseline for comparison?

7. **Dependencies & Risks**
   - What are the external dependencies?
   - What are the risks to delivery?
   - Are there regulatory or compliance considerations?

---

## Deploy (Deployment / Release)

For deployment plans, release checklists, and infrastructure change specs.

### Dimensions

1. **Change Description**
   - Is the change clearly described?
   - What systems/services are affected?
   - What's the expected impact on users?

2. **Pre-conditions**
   - Are all prerequisites listed?
   - Are dependency versions specified?
   - Is the environment state validated?

3. **Rollout Strategy**
   - Is the rollout phased (canary, blue-green, etc.)?
   - Are health checks defined?
   - What's the go/no-go criteria at each phase?

4. **Rollback Plan**
   - Is rollback clearly documented?
   - Has rollback been tested?
   - What's the maximum acceptable rollback time?
   - Are there data implications of rollback?

5. **Monitoring & Alerting**
   - What metrics should be watched during/after deploy?
   - Are alert thresholds defined?
   - Who is on-call?

6. **Communication**
   - Are stakeholders identified and notified?
   - Is there a user-facing changelog?
   - What's the escalation path?

7. **Post-deploy Validation**
   - What smoke tests should run?
   - How long is the observation period?
   - When is the deploy considered "complete"?

---

## Other (General Document)

For documents that don't fit the above categories.

### Dimensions

1. **Clarity** — Is the document well-structured and easy to follow?
2. **Completeness** — Does it cover the topic adequately?
3. **Accuracy** — Are claims supported by evidence?
4. **Actionability** — Does it lead to clear next steps?
5. **Audience** — Is it appropriate for the intended readers?
