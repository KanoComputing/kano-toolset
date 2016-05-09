/**
 *
 * kano_bindings.h
 *
 * Copyright (C) 2016 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Adds the interface between useful Kano Toolset functions and C++
 *
 *     kano.*
 *
 */


#ifndef __KANO_BINDINGS_H__
#define __KANO_BINDINGS_H__

#include <string>
#include <unordered_map>

#include <kano/python/python_helpers.h>

#define KANO_NETWORK "kano.network"
#define KANO_UTILS_AUDIO "kano.utils.audio"


namespace kano {

    class network : Binding {
        public:
            network();
            std::unordered_map<std::string, std::string> get_network_info() const;
    };

    namespace utils {
        class audio : Binding {
            public:
                audio();
                bool play_sound(const std::string audio_file, const bool background=false) const;
                long percent_to_millibel(const int percent, const bool raspberry_mod=false) const;
                long get_volume() const;
        };
    }

}


#endif
