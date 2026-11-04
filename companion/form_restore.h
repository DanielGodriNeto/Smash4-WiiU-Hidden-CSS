/* Pure restore rule for the experimental US v304 companion. No WUPS or wut includes, so a host compiler can test it. */
#ifndef HIDDEN_CSS_FORM_RESTORE_H
#define HIDDEN_CSS_FORM_RESTORE_H

#include <stdint.h>

typedef struct {
    uint32_t form;
    uint32_t base;
} form_restore_pair_t;

/* Hidden form IDs (fighter DB field 6) and the base fighter each one is assigned as its alternate. */
static const form_restore_pair_t form_restore_pairs[] = {
    {58u, 15u},
    {59u, 22u},
    {60u, 41u},
    {61u, 30u},
};

/* Returns the form ID only when kind is a table form AND alternate is that form's base.
 * Every other input returns alternate unchanged (fail closed). */
static inline uint32_t form_restore_alternate(uint32_t kind, uint32_t alternate) {
    uint32_t count = (uint32_t)(sizeof form_restore_pairs / sizeof form_restore_pairs[0]);
    for (uint32_t i = 0; i < count; ++i) {
        if (kind == form_restore_pairs[i].form) {
            return alternate == form_restore_pairs[i].base ? kind : alternate;
        }
    }
    return alternate;
}

#endif
