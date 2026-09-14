# MySQL change checklist

Use for contract-breaking, destructive, bulk-data, trigger/routine, or performance/locking-sensitive changes.

## Before

- [ ] Target DB engine/version known when behavior depends on it.
- [ ] Exact current schema inspected.
- [ ] Relevant application readers/writers identified.
- [ ] Related triggers/procedures/events inspected.
- [ ] Derived/denormalized field ownership identified.
- [ ] Table size/hotness known or explicitly marked unknown.
- [ ] Change classified: additive / behavioral / data / contract / destructive / lock-sensitive.
- [ ] Old/new code coexistence considered.
- [ ] Migration selection predicate and expected affected population defined.
- [ ] Rollback or forward-recovery strategy defined for risky changes.
- [ ] Existing backup/recovery status verified by the owning workflow when production execution requires it.

## During

- [ ] Prefer expand -> migrate -> contract when compatibility window helps.
- [ ] Bulk operations are bounded/restartable when scale/risk warrants it.
- [ ] No incidental schema cleanup mixed into the task.
- [ ] No application code writes fields intentionally maintained by DB logic.
- [ ] No destructive SQL runs without explicit scope/evidence.
- [ ] DDL locking/online behavior is not assumed from memory.

## After

- [ ] Resulting schema re-read.
- [ ] Expected affected row count checked.
- [ ] Representative migrated and untouched rows checked.
- [ ] Null/uniqueness/range/business invariants checked.
- [ ] Relevant write paths exercised.
- [ ] Trigger/procedure/derived-field behavior checked.
- [ ] Query plans checked when index/performance was part of the change.
- [ ] Compatibility checked across deployment phases where applicable.
- [ ] Any production/runtime verification not executed is stated explicitly.
