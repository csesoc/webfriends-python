/*
   Copyright 2013 John Wiseheart

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/


// for automatic popover placement
var getPlacementFunction = function (defaultPosition, width, height) {
    return function (tip, element) {
        var position, top, bottom, left, right;

        var $element = $(element);
        var boundTop = $(document).scrollTop();
        var boundLeft = $(document).scrollLeft();
        var boundRight = boundLeft + $(window).width();
        var boundBottom = boundTop + $(window).height();

        var pos = $.extend({}, $element.offset(), {
            width: element.offsetWidth,
            height: element.offsetHeight
        });

        var isWithinBounds = function (elPos) {
            return boundTop < elPos.top && boundLeft < elPos.left && boundRight > (elPos.left + width) && boundBottom > (elPos.top + height);
        };

        var testTop = function () {
            if (top === false) return false;
            top = isWithinBounds({
                top: pos.top - height,
                left: pos.left + pos.width / 2 - width / 2
            });
            return top ? "top" : false;
        };

        var testBottom = function () {
            if (bottom === false) return false;
            bottom = isWithinBounds({
                top: pos.top + pos.height,
                left: pos.left + pos.width / 2 - width / 2
            });
            return bottom ? "bottom" : false;
        };

        var testLeft = function () {
            if (left === false) return false;
            left = isWithinBounds({
                top: pos.top + pos.height / 2 - height / 2,
                left: pos.left - width
            });
            return left ? "left" : false;
        };

        var testRight = function () {
            if (right === false) return false;
            right = isWithinBounds({
                top: pos.top + pos.height / 2 - height / 2,
                left: pos.left + pos.width
            });
            return right ? "right" : false;
        };

        switch (defaultPosition) {
            case "top":
                if (position == testTop()) return position;
                break;
            case "bottom":
                if (position == testBottom()) return position;
                break;
            case "left":
                if (position == testLeft()) return position;
                break;
            case "right":
                if (position == testRight()) return position;
                break;
            default:
                if (position == testTop()) return position;
                if (position == testBottom()) return position;
                if (position == testLeft()) return position;
                if (position == testRight()) return position;
                return defaultPosition;
        }
    };
};

// pretty json

function syntaxHighlight(json) {
    if (typeof json != 'string') {
         json = JSON.stringify(json, undefined, 2);
    }
    json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
        var cls = 'number';
        if (/^"/.test(match)) {
            if (/:$/.test(match)) {
                cls = 'key';
            } else {
                cls = 'string';
            }
        } else if (/true|false/.test(match)) {
            cls = 'boolean';
        } else if (/null/.test(match)) {
            cls = 'null';
        }
        return '<span class="' + cls + '">' + match + '</span>';
    });
}


// make tabs work

$("#labTabs a").click(function (e) {
    $(this).tab("show");
    e.preventDefault();
});


// Deals with searching

$( "#searchButton" ).click(function() {
    var searchText = $('#searchText').val();
    $( '#searchResults' ).html("");
    if (searchText !== "") {
        for (var lab in lab_data) {
            if (lab_data[lab].online) {
                for (var user in lab_data[lab].users) {
                    if (lab_data[lab].users[user].user_id) {
                        var user_id = lab_data[lab].users[user].user_id;
                        var zid = lab_data[lab].users[user].zid;
                        var name = lab_data[lab].users[user].name;
                        if ((searchText==user_id)||(user_id.toLowerCase().indexOf(searchText.toLowerCase()) !== -1)||(name.toLowerCase().indexOf(searchText.toLowerCase()) !== -1)) {
                            var foundText = "<small><strong>"+name+"</strong>: "+ lab + user + "</small><br />";
                            $( '#searchResults' ).append(foundText);
                            $('#' + lab + user).find('div').find('div').toggle("highlight");
                            $('#' + lab + user).find('div').find('div').toggle("highlight");

                            console.log(lab_data[lab].users[user].name);
                        }
                        $("#searchResults").css({'display':'inherit'});
                    }
                }
            }
        }
        if ($("#searchResults").text()==="") {
            $("#searchResults").html("<small>No results found.</small>");
        }
    } else {
        $("#searchResults").css({'display':'none'});
    }
});

$(function() {
    // Deals with persisten tabs (kinda)
    var hash = window.location.hash;
    hash && $('ul.nav a[href="' + hash + '"]').tab('show');
    window.scrollTo(0, 0);
    $('#labTabs a').click(function (e) {
        $(this).tab('show');
        window.scrollTo(0, 0);
        window.location.hash = this.hash;
        window.scrollTo(0, 0);
    });

    // Server list
    $("#users-list").html(getUserList($('#server-select').val()));
    $.bootstrapSortable();

    // Deals with resizing the search box so it doesnt look strange
    $("#searchResults").css({'max-height':(($("#content").height()-50)+'px')});
    
    // Debug pretty JSON
    jQuery.fn.exists = function(){return this.length>0;};
    if ($('#lab_data').exists()) {
        $('#lab_data').html(syntaxHighlight(JSON.stringify(lab_data, undefined, '\t')));
        $('#server_data').html(syntaxHighlight(JSON.stringify(server_data, undefined, '\t')));
    }
});

// Deals with resizing the search box so it doesnt look strange
$("#content").resize(function(e){
    $("#searchResults").css({'max-height':(($("#content").height()-50)+'px')});
});


// Searches on keypress
$('#searchText').keyup(function(e){
        $('#searchButton').click();
});

// Puts a popup over all the boxes (that require popups)
for (var lab in lab_data) {
    if (lab_data[lab].online) {
        for (var user in lab_data[lab].users) {
            if (lab_data[lab].users[user].user_id) {
                var user_id = lab_data[lab].users[user].user_id;
                var zid = lab_data[lab].users[user].zid;
                var uname = lab_data[lab].users[user].name;
                var degree = lab_data[lab].users[user].degree;
                var since = lab_data[lab].users[user].since_string;

                var title =  uname;

                var content = "ID: "+ user_id + "<br />";
                content = content + (zid ? "zID: " + zid + "<br />" : "" );
                content = content + (degree ? "Degree: " + degree + "<br />" : "" );
                content = content + (since ? "Since: " + since + "<br />" : "" );

                $("#" + lab + user ).popover({  container:'.tab-content',
                                                placement:  getPlacementFunction("top", 300, 300),
                                                content:content,
                                                title:title,
                                                html:true,
                                                trigger:'hover'});
            }
        }
    }
}

// generate the list of users for each lab/sever
var getUserList = function(selected) {
    var userlist = "";
    var picked = 0;
    var user = "";
    if (selected in server_data) {
        for (user in server_data[selected].users) {
            userlist = userlist + '<tr><td>' + server_data[selected].users[user].user_id + '</td><td>' +
            server_data[selected].users[user].name + '</td><td data-dateformat="H:m:s DD/MM">' + server_data[selected].users[user].since_string + '</td></tr>';
            
        }
    } else if (selected in lab_data) {
        for (user in lab_data[selected].users) {
            if (lab_data[selected].users[user].user_id) {
                userlist = userlist + '<tr><td>' + lab_data[selected].users[user].user_id + '</td><td>' +
                lab_data[selected].users[user].name + '</td><td data-dateformat="H:m:s DD/MM">' + lab_data[selected].users[user].since_string + '</td></tr>';
            }
        }
    } else if (selected == "all-labs") {
        for (var lab in lab_data) {
            for (user in lab_data[lab].users) {
                if (lab_data[lab].users[user].user_id) {
                    userlist = userlist + '<tr><td>' + lab_data[lab].users[user].user_id + '</td><td>' +
                    lab_data[lab].users[user].name + '</td><td data-dateformat="H:m:s DD/MM">' + lab_data[lab].users[user].since_string + '</td></tr>';
                }
            }
        }
    }


    if (userlist==="") {
        userlist = "<span style='font-size:11px'>No users in this lab.</span>";
    } else {
        userlist = ["<table style='font-size:11px' class='table table-striped table-bordered sortable'>",
                        "<thead>",
                            "<tr>",
                                "<th>CSE ID</th>",
                                "<th>Name</th>",
                                "<th data-defaultsort='desc'>Logged on Since</th>",
                            "</tr>",
                        "</thead>",
                        "<tbody>",
                        userlist ,
                        "</tbody>",
                    "</table>"].join('\n');
    }
    return userlist;
};

//make the select input pretty
$("select").selectpicker({style: 'btn-lg btn-primary', menuStyle: 'dropdown-inverse'});

//change the user table when a different lab is selected
$( "#server-select" ).change(function() {
    $("#users-list").html(getUserList($(this).val()));
    $.bootstrapSortable(true);
});


