/*
    internal_unwind.h

    Copyright (C) 2012  Red Hat, Inc.

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
*/
#ifndef SATYR_INTERNAL_UNWIND_H
#define SATYR_INTERNAL_UNWIND_H

#include <libelf.h>
#include <gelf.h>
#include <elfutils/libdwfl.h>

#include "config.h"

/* define macros indicating what unwinder are we using */
#if (defined HAVE_LIBELF_H && defined HAVE_GELF_H && defined HAVE_LIBELF && defined HAVE_LIBDW && defined HAVE_ELFUTILS_LIBDWFL_H && defined HAVE_DWFL_FRAME_STATE_CORE)
#  define WITH_LIBDWFL
#endif

#if !defined WITH_LIBDWFL && (defined HAVE_LIBUNWIND && defined HAVE_LIBUNWIND_COREDUMP && defined HAVE_LIBUNWIND_GENERIC && defined HAVE_LIBUNWIND_COREDUMP_H && defined HAVE_LIBELF_H && defined HAVE_GELF_H && defined HAVE_LIBELF && defined HAVE_LIBDW && defined HAVE_ELFUTILS_LIBDWFL_H)
#  define WITH_LIBUNWIND
#endif

/* Error/warning reporting macros. Allows the error reporting code to be less
 * verbose with the restrictions that:
 *  - pointer to error message pointer must be always named "error_msg"
 *  - the variable "elf_file" must always contain the filename that is operated
 *    on by the libelf
 */
#define set_error(fmt, ...) _set_error(error_msg, fmt, ##__VA_ARGS__)
#define set_error_dwfl(func) _set_error(error_msg, "%s failed: %s", \
        func, dwfl_errmsg(-1))
#define set_error_elf(func) _set_error(error_msg, "%s failed for '%s': %s", \
        func, elf_file, elf_errmsg(-1))
#define warn_elf(func) warn("%s failed for '%s': %s", \
        func, elf_file, elf_errmsg(-1))

void
_set_error(char **error_msg, const char *fmt, ...) __sr_printf(2, 3);

/* internal linked list manipulation */
#define list_append(head,tail,item)          \
    do{                                      \
        if (head == NULL)                    \
        {                                    \
            head = tail = item;              \
        }                                    \
        else                                 \
        {                                    \
            tail->next = item;               \
            tail = tail->next;               \
        }                                    \
    } while(0)

struct exe_mapping_data
{
    uint64_t start;
    char *filename;
    struct exe_mapping_data *next;
};

struct core_handle
{
    int fd;
    Elf *eh;
    Dwfl *dwfl;
    Dwfl_Callbacks cb;
    struct exe_mapping_data *segments;
};

/* Gets dwfl handle and executable map data to be used for unwinding. The
 * executable map is only used by libunwind. */
struct core_handle *
open_coredump(const char *elf_file, const char *exe_file, char **error_msg);

void
core_handle_free(struct core_handle *ch);

struct sr_core_frame *
resolve_frame(Dwfl *dwfl, Dwarf_Addr ip, bool minus_one);

short
get_signal_number(Elf *e, const char *elf_file);

#endif /* SATYR_INTERNAL_UNWIND_H */
