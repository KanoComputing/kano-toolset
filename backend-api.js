// Client part of the browser backend-api library
// Copyright (C) 2014 Radek Pazdera, Kano Computing Inc.
//
// This program is free software; you can redistribute it and/or
// modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
// 02110-1301, USA.

window.backend = {
    callbacks: [],

    call: function () {
        if (arguments.length >= 1) {
            func = arguments[0];
            args = [];

            if (arguments.length > 1 &&
                typeof arguments[arguments.length - 1] === 'function') {
                
                arguments = Array.prototype.slice.call(arguments, 0);
                callback = arguments.pop();
            	timestamp = (new Date).getTime();

                this.callbacks.push({
                    timestamp: timestamp,
                    func: func,
                    callback: callback
                });
                func += "[" + timestamp + "]";
            }

            for (var i = 1; i < arguments.length; i += 1) {
                args.push(encodeURIComponent(arguments[i].toString()));
            }

        } else {
            func = 'error';
            args = [encodeURIComponent('Invalid API call - no arguments passed.')];
        }

        var args_string = args.join('/');

        window.location.hash = 'api:' + func + '/' + args_string;
    },
}
