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
                if (position = testTop()) return position;
            case "bottom":
                if (position = testBottom()) return position;
            case "left":
                if (position = testLeft()) return position;
            case "right":
                if (position = testRight()) return position;
            default:
                if (position = testTop()) return position;
                if (position = testBottom()) return position;
                if (position = testLeft()) return position;
                if (position = testRight()) return position;
                return defaultPosition;
        }
    }
};


// make tabs work

$("#labTabs a").click(function (e) {
    $(this).tab("show");
    e.preventDefault();
});


// Deals with searching

$( "#searchButton" ).click(function() {
    var searchText = $('#searchText').val()
    $( '#searchResults' ).html("");
    if (searchText!="") {
        $(".comp").each(function() {
            if ($(this).data("user-id")) {
                if ((searchText==$(this).data("user-id"))||(searchText==$(this).data("user-zid"))||($(this).data("user-name").toLowerCase().indexOf(searchText.toLowerCase()) !== -1)) {
                    var foundText = "<small><strong>"+$(this).data("user-name")+"</strong>: "+$(this).attr('id')+ "</small><br />";
                    $( '#searchResults' ).append($(foundText));
                        $(this).find('div').find('div').toggle("highlight");
                        $(this).find('div').find('div').toggle("highlight");
                }
                $("#searchResults").css({'display':'inherit'});
            }
        });
        if ($("#searchResults").text()=="") {
            $("#searchResults").html("<small>No results found.</small>")
        }
    } else {
        $("#searchResults").css({'display':'none'});
    }
});

// Deals with resizing the search box so it doesnt look strange
// Also deals with persisten tabs (kinda)
$(function() {

    var hash = window.location.hash;
    hash && $('ul.nav a[href="' + hash + '"]').tab('show');
    window.scrollTo(0, 0);
    $('#labTabs a').click(function (e) {
        $(this).tab('show');
        var scrollmem = $('body').scrollTop();
        window.location.hash = this.hash;
        $('html,body').scrollTop(scrollmem);
    });

    $("#searchResults").css({'max-height':(($("#content").height()-50)+'px')});
});
$("#content").resize(function(e){
    $("#searchResults").css({'max-height':(($("#content").height()-50)+'px')});
});


// Deals with enter press in search box

$('#searchText').keyup(function(e){
        $('#searchButton').click();
});

// Puts a popup over all the boxes (that require popups)

$( ".comp" ).each(function() {
    if ($(this).data("user-id")) {
        var content = " ID: "+$(this).data("user-id")+"<br />";
        if ($(this).data("user-zid")) {
            content = content + "zID: "+$(this).data("user-zid")+"<br />";
        }
        if ($(this).data("user-since")) {
            content = content + "Since: "+$(this).data("user-since")+"<br />";
        }
        if ($(this).data("user-degree")) {
            content = content + "Degree: "+$(this).data("user-degree");
        }
    
        title =  $(this).data("user-name");

        $(this).popover({   container:'.tab-content',
                            placement:  getPlacementFunction("top", 300, 300),
                            content:content,
                            title:title,
                            html:true,
                            trigger:'hover'});
    }

    content = "You can search for people based on their name, cse username and even zid."

// $('#searchGroup').popover({   container:'body',
//                             placement: 'top',
//                             content:content,
//                             delay:5000,
//                             title:"Search Tips",
//                             html:true,
//                             trigger:'hover'});

});
