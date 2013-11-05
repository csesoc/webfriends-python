// for automatic popover placement
function autoPlacement(tip, element) {
    var $element, above, actualHeight, actualWidth, below, boundBottom, boundLeft, boundRight, boundTop, elementAbove, elementBelow, elementLeft, elementRight, isWithinBounds, left, pos, right;
    isWithinBounds = function(elementPosition) {
        return boundTop < elementPosition.top && boundLeft < elementPosition.left && boundRight > (elementPosition.left + actualWidth) && boundBottom > (elementPosition.top + actualHeight);
    };
    $element = $(element);
    pos = $.extend({}, $element.offset(), {
        width: element.offsetWidth,
        height: element.offsetHeight
    });
    actualWidth = 283;
    actualHeight = 180;
    boundTop = $(document).scrollTop();
    boundLeft = $(document).scrollLeft();
    boundRight = boundLeft + $(window).width();
    boundBottom = boundTop + $(window).height();
    elementAbove = {
        top: pos.top - actualHeight,
        left: pos.left + pos.width / 2 - actualWidth / 2
    };
    elementBelow = {
        top: pos.top + pos.height,
        left: pos.left + pos.width / 2 - actualWidth / 2
    };
    elementLeft = {
         top: pos.top + pos.height / 2 - actualHeight / 2,
         left: pos.left - actualWidth
    };
    elementRight = {
        top: pos.top + pos.height / 2 - actualHeight / 2,
        left: pos.left + pos.width
    };
    above = isWithinBounds(elementAbove);
    below = isWithinBounds(elementBelow);
    left = isWithinBounds(elementLeft);
    right = isWithinBounds(elementRight);
    if (above) {
        return "top";
    } else if (below) {
        return "bottom";
    } else if (left) {
        return "left";
    } else {
        return "right";
    }
}


// Sorts out persistent tabs

$("#labTabs a").click(function (e) {
    e.preventDefault()
    $(this).tab("show")
})

$("ul#labTabs > li > a").on("shown.bs.tab", function (e) {
    var id = $(e.target).attr("href").substr(1);
    window.location.hash = id;
});

var hash = window.location.hash;
$('#labTabs a[href="' + hash + '"]').tab('show');
if (hash) {
    window.scrollTo(0, 0);
    setTimeout(function() {
            window.scrollTo(0, 0);     // run it a bit later also for browser compatibility
        }, 1);
}


// Deals with searching

$( "#searchButton" ).click(function() {
    var searchText = $('#searchText').val()
    $( '#searchResults' ).html("");
    if (searchText!="") {
        $(".comp-open").each(function() {
            if ((searchText==$(this ).data("user-id"))||(searchText==$(this ).data("user-zid"))||($(this ).data("user-name").toLowerCase().indexOf(searchText.toLowerCase()) !== -1)) {
                var foundText = "<small><strong>"+$(this ).data("user-name")+"</strong>: "+$(this ).attr('id')+ "</small><br />";
                $( '#searchResults' ).append($(foundText));
            } 
            $("#searchResults").css({'display':'inherit'});
        });
        if ($("#searchResults").text()=="") {
            $("#searchResults").html("<small>No results found.</small>")
        }
    } else {
        $("#searchResults").css({'display':'none'});
    }
});

// Deals with resizing the search box so it doesnt look strange

$(function() {
    $("#searchResults").css({'max-height':(($("#content").height()-50)+'px')});
});
$("#content").resize(function(e){
    $("#searchResults").css({'max-height':(($("#content").height()-50)+'px')});
});


// Deals with enter press in search box

$('#searchText').keyup(function(e){
    if(e.keyCode == 13) {
        $('#searchButton').click();
    }
});

// Puts a popup over all the boxes (that require popups)

$( ".comp-open" ).each(function() {
    if ($(this).data("user-id")) {
        var content = " ID: "+$(this).data("user-id")+"<br /> \
                    zID: "+$(this).data("user-zid")+"<br /> \
                    Since: "+$(this).data("user-since")+"<br />";
        if ($(this).data("user-degree")) {
            content = content+ "Degree: "+$(this).data("user-degree");
        }
    
        title =  $(this).data("user-name");

        $(this).popover({   container:'.tab-content',
                            placement: autoPlacement,
                            content:content,
                            title:title,
                            html:true,
                            trigger:'hover'});
    }
});