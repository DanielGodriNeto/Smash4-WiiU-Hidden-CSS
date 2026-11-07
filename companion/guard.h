/* Pure decision rules for the experimental US v304 companion. companion/main.c is the WUPS adapter.
 * No WUPS, wut or FunctionPatcher includes: tests/guard_host_harness.c compiles this header on a host.
 * Every function is static inline so an unused rule cannot trigger -Wunused-function under -Werror. */
#ifndef HIDDEN_CSS_GUARD_H
#define HIDDEN_CSS_GUARD_H

#include <stdbool.h>
#include <stdint.h>
#include "form_restore.h"

/* US base title ID. The update version is not read here: v304 is enforced by the 304, 304 version
 * arguments passed to FunctionPatcher in main.c (not verified on hardware) and by the code signatures below. */
#define GUARD_TITLE_US_V304 UINT64_C(0x0005000010144F00)

/* Forms whose assignment-site guard is verified, as a bit per form ID (fighter DB field 6).
 * The hook writes only for set bits. Only form 58 (Giga Bowser) is set, because only its assignment
 * block (0x02E45708) has a signature. To enable 59, 60 or 61: add that site's verified words and a
 * separate check in main.c, then set the form's bit here, then update docs/RESPAWN-COMPANION.md. */
#define GUARD_ENABLED_FORMS_MASK (UINT64_C(1) << 58)

/* Default for the plugin setting when no value is stored. Default OFF, experimental. */
#define GUARD_DEFAULT_ENABLED false

/* Entry fields read by the hook: kind at +0x10 and alternate at +0x14, so the reads end at +0x18. */
#define GUARD_ENTRY_SPAN UINT32_C(0x18)

/* ASSUMPTION, not verified on hardware: the fighter entry lies in the range reported by
 * OSGetMapVirtAddrRange(). wut documents that call only as the range available for mapping. */
#define GUARD_ADDRESS_END UINT64_C(0x100000000)

/* Two 16-byte windows: the initializer signature (4 words) and the Giga assignment signature (4 words). */
#define GUARD_SIGNATURE_WORDS 8u
#define GUARD_WINDOW_BYTES 16u

static const uint32_t guard_entry_signature[4] = {0x7C0802A6u, 0x9421FFF0u, 0x93E1000Cu, 0x7C7F1B78u};
static const uint32_t guard_assign_signature[4] = {0x398000CCu, 0x3800000Fu, 0x999F14EEu, 0x901F0014u};

typedef enum guard_reason {
    GUARD_OK = 0,
    GUARD_TITLE_MISMATCH,
    GUARD_EXECUTABLE_NOT_FOUND,
    GUARD_BOUNDS_FAILED,
    GUARD_SIGNATURE_MISMATCH,
    GUARD_RANGE_UNKNOWN,
    GUARD_LIB_INIT_FAILED,
    GUARD_PATCH_ADD_FAILED,
    GUARD_PATCH_NOT_APPLIED,
    GUARD_PATCH_HANDLE_NULL,
    GUARD_REMOVE_FAILED,
    GUARD_STUCK,
    GUARD_CONFIG_OFF,
} guard_reason_t;

static inline bool guard_title_allowed(uint64_t title_id) {
    return title_id == GUARD_TITLE_US_V304;
}

static inline bool guard_form_enabled(uint32_t kind) {
    return kind < 64u && ((GUARD_ENABLED_FORMS_MASK >> kind) & UINT64_C(1)) != 0u;
}

/* True when the window [addr, addr + 16) lies inside [text_addr, text_addr + text_size) and the
 * 32-bit address space. All arithmetic is 64-bit, so nothing wraps. */
static inline bool guard_window_in_text(uint32_t text_addr, uint32_t text_size, uint32_t addr) {
    uint64_t text_end = (uint64_t)text_addr + text_size;
    uint64_t window_end = (uint64_t)addr + GUARD_WINDOW_BYTES;
    return text_size >= GUARD_WINDOW_BYTES && text_end <= GUARD_ADDRESS_END &&
           addr >= text_addr && window_end <= text_end;
}

static inline bool guard_bounds_ok(uint32_t text_addr, uint32_t text_size,
                                   uint32_t entry_addr, uint32_t assign_addr) {
    return guard_window_in_text(text_addr, text_size, entry_addr) &&
           guard_window_in_text(text_addr, text_size, assign_addr);
}

/* words[0..3] are the initializer, words[4..7] the Giga assignment block. */
static inline bool guard_signature_ok(const uint32_t words[GUARD_SIGNATURE_WORDS]) {
    for (uint32_t i = 0; i < 4u; ++i) {
        if (words[i] != guard_entry_signature[i] || words[4u + i] != guard_assign_signature[i]) {
            return false;
        }
    }
    return true;
}

static inline bool guard_range_ok(uint32_t range_lo, uint32_t range_size) {
    return range_size != 0u && (uint64_t)range_lo + range_size <= GUARD_ADDRESS_END;
}

/* Rejects NULL, misaligned pointers, anything below the range, and any entry whose last read
 * (entry + 0x18, exclusive) passes the range end. 64-bit math, so 0xFFFFFFFC cannot wrap. */
static inline bool guard_entry_ptr_ok(uint32_t entry, uint32_t range_lo, uint32_t range_size) {
    uint64_t last = (uint64_t)entry + GUARD_ENTRY_SPAN;
    uint64_t range_end = (uint64_t)range_lo + range_size;
    if (!guard_range_ok(range_lo, range_size)) return false;
    if (entry == 0u || (entry & 3u) != 0u) return false;
    return entry >= range_lo && last <= range_end;
}

/* True when the hook may dereference entry: the hook is enabled and the pointer passes the validator. */
static inline bool guard_may_read_entry(bool enabled, uint32_t entry, uint32_t range_lo, uint32_t range_size) {
    return enabled && guard_entry_ptr_ok(entry, range_lo, range_size);
}

/* The alternate to store for an entry of this kind. Equals current unless the form is enabled and
 * current is exactly that form's base, so a caller that writes only on a difference never writes otherwise. */
static inline uint32_t guard_restored_alternate(uint32_t kind, uint32_t current) {
    return guard_form_enabled(kind) ? form_restore_alternate(kind, current) : current;
}

/* Adapter-supplied facts. main.c fills them; guard_preflight decides. */
typedef struct guard_facts {
    uint64_t title_id;
    bool executable_found;
    bool bounds_ok;
    bool signature_ok;
    uint32_t range_lo;
    uint32_t range_size;
} guard_facts_t;

static inline guard_reason_t guard_preflight(const guard_facts_t *facts) {
    if (!guard_title_allowed(facts->title_id)) return GUARD_TITLE_MISMATCH;
    if (!facts->executable_found) return GUARD_EXECUTABLE_NOT_FOUND;
    if (!facts->bounds_ok) return GUARD_BOUNDS_FAILED;
    if (!facts->signature_ok) return GUARD_SIGNATURE_MISMATCH;
    if (!guard_range_ok(facts->range_lo, facts->range_size)) return GUARD_RANGE_UNKNOWN;
    return GUARD_OK;
}

/* enabled is read by the hook, so it is volatile. Only guard_enable and guard_disable write it. */
typedef struct guard_state {
    volatile bool enabled;
    bool lib_ready;
    bool has_handle;
    uint32_t handle;
} guard_state_t;

/* Injected FunctionPatcher operations. Each returns true on success. */
typedef struct guard_ops {
    bool (*init_library)(void);
    bool (*add_patch)(uint32_t *handle, bool *applied);
    bool (*remove_patch)(uint32_t handle);
    void (*deinit_library)(void);
    void (*log)(guard_reason_t reason);
} guard_ops_t;

static inline const char *guard_reason_text(guard_reason_t reason) {
    switch (reason) {
    case GUARD_OK:
        return "[HiddenCSS] Experimental hidden-form respawn hook active for US v304.\n";
    case GUARD_TITLE_MISMATCH:
        return "[HiddenCSS] US v304 respawn hook was not applied: title is not US v304.\n";
    case GUARD_EXECUTABLE_NOT_FOUND:
        return "[HiddenCSS] US v304 respawn hook was not applied: cross_f module not found.\n";
    case GUARD_BOUNDS_FAILED:
        return "[HiddenCSS] US v304 respawn hook was not applied: guard addresses outside module text.\n";
    case GUARD_SIGNATURE_MISMATCH:
        return "[HiddenCSS] US v304 respawn hook was not applied: code signature mismatch.\n";
    case GUARD_RANGE_UNKNOWN:
        return "[HiddenCSS] US v304 respawn hook was not applied: entry address range unknown.\n";
    case GUARD_LIB_INIT_FAILED:
        return "[HiddenCSS] US v304 respawn hook was not applied: FunctionPatcher init failed.\n";
    case GUARD_PATCH_ADD_FAILED:
        return "[HiddenCSS] US v304 respawn hook was not applied: patch add failed.\n";
    case GUARD_PATCH_NOT_APPLIED:
        return "[HiddenCSS] US v304 respawn hook was not applied.\n";
    case GUARD_PATCH_HANDLE_NULL:
        return "[HiddenCSS] US v304 respawn hook was not applied: no patch handle.\n";
    case GUARD_REMOVE_FAILED:
        return "[HiddenCSS] Hook removal failed.\n";
    case GUARD_STUCK:
        return "[HiddenCSS] Hook removal is pending; respawn hook stays disabled.\n";
    case GUARD_CONFIG_OFF:
        return "[HiddenCSS] Respawn hook inactive: disabled in plugin settings.\n";
    }
    return "[HiddenCSS] Unknown hook state.\n";
}

/* Removes the held patch and deinitializes the library. Returns false, keeping both, if removal fails. */
static inline bool guard_release(guard_state_t *st, const guard_ops_t *ops) {
    if (st->has_handle) {
        if (!ops->remove_patch(st->handle)) return false;
        st->has_handle = false;
        st->handle = 0u;
    }
    if (st->lib_ready) {
        ops->deinit_library();
        st->lib_ready = false;
    }
    return true;
}

static inline guard_reason_t guard_rollback(guard_state_t *st, const guard_ops_t *ops, guard_reason_t reason) {
    st->enabled = false;
    ops->log(reason);
    if (!guard_release(st, ops)) ops->log(GUARD_REMOVE_FAILED);
    return reason;
}

static inline void guard_disable(guard_state_t *st, const guard_ops_t *ops) {
    st->enabled = false;
    if (!guard_release(st, ops)) ops->log(GUARD_REMOVE_FAILED);
}

/* All or nothing: any failure leaves enabled=false and no patch held. */
static inline guard_reason_t guard_enable(guard_state_t *st, const guard_ops_t *ops, const guard_facts_t *facts) {
    guard_reason_t reason;
    bool applied = false;
    if (st->enabled) return GUARD_OK;
    if (st->has_handle) {
        ops->log(GUARD_STUCK);
        return GUARD_STUCK;
    }
    reason = guard_preflight(facts);
    if (reason != GUARD_OK) {
        st->enabled = false;
        ops->log(reason);
        return reason;
    }
    if (!ops->init_library()) {
        ops->log(GUARD_LIB_INIT_FAILED);
        return GUARD_LIB_INIT_FAILED;
    }
    st->lib_ready = true;
    st->handle = 0u;
    bool added = ops->add_patch(&st->handle, &applied);
    st->has_handle = st->handle != 0u;
    if (!added) return guard_rollback(st, ops, GUARD_PATCH_ADD_FAILED);
    if (!applied) return guard_rollback(st, ops, GUARD_PATCH_NOT_APPLIED);
    if (!st->has_handle) return guard_rollback(st, ops, GUARD_PATCH_HANDLE_NULL);
    st->enabled = true;
    ops->log(GUARD_OK);
    return GUARD_OK;
}

/* Resolves the stored plugin setting. Read error (any storage failure) fails closed to false.
 * A missing key takes GUARD_DEFAULT_ENABLED. Otherwise the stored value is used. */
static inline bool guard_config_resolve(bool read_ok, bool found, bool stored) {
    if (!read_ok) return false;
    if (!found) return GUARD_DEFAULT_ENABLED;
    return stored;
}

/* Applies the resolved setting. wanted=false always tears down: the patch is removed before
 * enabled is cleared, and a removal failure is kept and logged by guard_disable. */
static inline guard_reason_t guard_apply(guard_state_t *st, const guard_ops_t *ops,
                                         const guard_facts_t *facts, bool wanted) {
    if (!wanted) {
        guard_disable(st, ops);
        ops->log(GUARD_CONFIG_OFF);
        return GUARD_CONFIG_OFF;
    }
    return guard_enable(st, ops, facts);
}

#endif
