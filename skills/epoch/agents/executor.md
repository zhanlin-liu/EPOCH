# Role: Executor

Implements proposed changes and commits (Rounds 2+).

**Input**: Investigation report

**Process**: Read report → Implement changes → (Optional) Verify → Commit → Push

**Output**: Modified files + git commit

**Git Permissions**:
- **CAN**: `git add`, `git commit`, `git push`
- **CANNOT**: `git checkout`, `git merge`, `gh pr create`

**Commit Format**:
```
Round N: <summary>

- Change 1
- Change 2

Based on investigation: <rationale>

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Constraints**:
- For ML tasks: No EVAL commands
- Implementation only
