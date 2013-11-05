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
    actualHeight = 117;
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


// Deals with searching

$( "#searchButton" ).click(function() {
    var searchText = $('#searchText').val()
    var foundText = "The user "+searchText+" could not be found";
    $( '#searchResults' ).html("");

     if (searchText!="") {
        $(".comp-open").each(function() {
            if ((searchText==$(this ).data("userid"))||(searchText==$(this ).data("userzid"))||($(this ).data("username").toLowerCase().indexOf(searchText.toLowerCase()) !== -1)) {
                var foundText = "<small><b>"+$(this ).data("username")+"</b>: "+$(this ).attr('id')+ "</small><br />";
                var pre = $( '#searchResults' ).html();
                $( '#searchResults' ).html( pre + foundText);
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
    if ($(this).data("userid")) {
        var content = " ID: "+$(this).data("userid")+"<br /> \
                    zID: "+$(this).data("userzid")+"<br /> \
                    Since: "+$(this).data("since")+"<br />";
        if ($(this).data( "degree" )) {
            content = content+ "Degree: "+$(this).data("degree");
        }
    
        title =  $(this).data("username");

        $(this).popover({   container:'.tab-content',
                            placement: autoPlacement,
                            content:content,
                            title:title,
                            html:true,
                            trigger:'hover'});
    }
});