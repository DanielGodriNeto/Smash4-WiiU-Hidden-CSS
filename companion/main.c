/* Experimental US v304 Aroma companion. No Nintendo code is bundled. */
#include <wups.h>
#undef DECL_FUNCTION
#include <function_patcher/function_patching.h>
#include <coreinit/debug.h>
#include <coreinit/dynload.h>
#include <coreinit/memorymap.h>
#include <coreinit/title.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include "guard.h"

WUPS_PLUGIN_NAME("Hidden CSS Giga Respawn (experimental)");
WUPS_PLUGIN_DESCRIPTION("US v304 only, experimental: restore hidden forms 58-61 after entry init (KO only seen for Giga Bowser)");
WUPS_PLUGIN_VERSION("0.1.0-experimental");
WUPS_PLUGIN_AUTHOR("CSS Expansion Contributors");
WUPS_PLUGIN_LICENSE("MIT");

#define ENTRY_INIT_ADDRESS 0x02E45558u
#define GIGA_ASSIGNMENT_ADDRESS 0x02E45708u

static uint32_t (*real_initialize_entry)(void *);
static guard_state_t guard_state;
static const uint64_t allowed_titles[] = {GUARD_TITLE_US_V304};
static const char *target_name;
static uint32_t target_offset;
static uint32_t entry_range_lo;
static uint32_t entry_range_size;
static FunctionPatcherStatus last_remove_status;

static uint32_t my_initialize_entry(void *entry) {
    /* Preserve the native r3 return even if callers treat this routine as void. */
    uint32_t result = real_initialize_entry(entry);
    if (!guard_may_read_entry(guard_state.enabled, (uint32_t)(uintptr_t)entry, entry_range_lo, entry_range_size)) return result;
    volatile uint32_t *kind = (volatile uint32_t *)((uint8_t *)entry + 0x10);
    volatile uint32_t *alternate = (volatile uint32_t *)((uint8_t *)entry + 0x14);
    uint32_t kind_value = *kind;
    uint32_t current = *alternate;
    uint32_t restored = guard_restored_alternate(kind_value, current);
    if (restored != current) {
        *alternate = restored;
    }
    return result;
}

static bool code_matches(void) {
    const volatile uint32_t *start = (const volatile uint32_t *)ENTRY_INIT_ADDRESS;
    const volatile uint32_t *assignment = (const volatile uint32_t *)GIGA_ASSIGNMENT_ADDRESS;
    uint32_t words[GUARD_SIGNATURE_WORDS];
    for (uint32_t i = 0; i < 4u; ++i) {
        words[i] = start[i];
        words[4u + i] = assignment[i];
    }
    return guard_signature_ok(words);
}

static bool find_executable(uint32_t *text_addr, uint32_t *text_size, const char **name) {
    int count = OSDynLoad_GetNumberOfRPLs();
    if (count <= 0 || count > 256) return false;
    for (int i = 0; i < count; ++i) {
        OSDynLoad_NotifyData module;
        if (!OSDynLoad_GetRPLInfo((uint32_t)i, 1, &module) || module.name == NULL) continue;
        const char *base = strrchr(module.name, '/');
        base = base ? base + 1 : module.name;
        if (strcmp(base, "cross_f.rpx") != 0 && strcmp(base, "cross_f") != 0) continue;
        *text_addr = module.textAddr;
        *text_size = module.textSize;
        *name = strcmp(base, "cross_f.rpx") == 0 ? "cross_f.rpx" : "cross_f";
        return true;
    }
    return false;
}

/* Gathers preflight facts. Memory is read only after the title matches and the bounds pass. */
static void collect_facts(guard_facts_t *facts) {
    uint32_t text_addr = 0u;
    uint32_t text_size = 0u;
    const char *name = NULL;
    facts->title_id = OSGetTitleID();
    if (!guard_title_allowed(facts->title_id)) return;
    facts->executable_found = find_executable(&text_addr, &text_size, &name);
    facts->bounds_ok = facts->executable_found &&
        guard_bounds_ok(text_addr, text_size, ENTRY_INIT_ADDRESS, GIGA_ASSIGNMENT_ADDRESS);
    facts->signature_ok = facts->bounds_ok && code_matches();
    OSGetMapVirtAddrRange(&facts->range_lo, &facts->range_size);
    if (facts->bounds_ok) {
        target_name = name;
        target_offset = ENTRY_INIT_ADDRESS - text_addr;
    }
    entry_range_lo = facts->range_lo;
    entry_range_size = facts->range_size;
}

static bool op_init_library(void) {
    return FunctionPatcher_InitLibrary() == FUNCTION_PATCHER_RESULT_SUCCESS;
}

static void op_deinit_library(void) {
    FunctionPatcher_DeInitLibrary();
}

static bool op_add_patch(uint32_t *handle, bool *applied) {
    function_replacement_data_t replacement =
        REPLACE_FUNCTION_OF_EXECUTABLE_BY_ADDRESS_WITH_VERSION(initialize_entry,
            allowed_titles, 1, target_name, target_offset, 304, 304);
    return FunctionPatcher_AddFunctionPatch(&replacement, handle, applied) == FUNCTION_PATCHER_RESULT_SUCCESS;
}

static bool op_remove_patch(uint32_t handle) {
    last_remove_status = FunctionPatcher_RemoveFunctionPatch(handle);
    return last_remove_status == FUNCTION_PATCHER_RESULT_SUCCESS;
}

static void op_log(guard_reason_t reason) {
    if (reason == GUARD_REMOVE_FAILED) {
        OSReport("[HiddenCSS] Hook removal failed: %s\n", FunctionPatcher_GetStatusStr(last_remove_status));
        return;
    }
    OSReport("%s", guard_reason_text(reason));
}

static const guard_ops_t guard_ops = {op_init_library, op_add_patch, op_remove_patch, op_deinit_library, op_log};

ON_APPLICATION_START() {
    guard_disable(&guard_state, &guard_ops);
    guard_facts_t facts = {0};
    collect_facts(&facts);
    guard_enable(&guard_state, &guard_ops, &facts);
}

ON_APPLICATION_ENDS() { guard_disable(&guard_state, &guard_ops); }
DEINITIALIZE_PLUGIN() { guard_disable(&guard_state, &guard_ops); }
