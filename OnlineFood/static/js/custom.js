let autocomplete;

function initAutoComplete(){
autocomplete = new google.maps.places.Autocomplete(
    // here id_address is added by django forms to identify address field
    document.getElementById('id_address'),
    {
        // geocode means address, establishment are business addresses like hotels, restaurants, offices
        types: ['geocode', 'establishment'],
        //default in this app is "IN" - add your country code. We can other countries as well
        componentRestrictions: {'country': ['in']},
    })
// function to specify what should happen when the prediction is clicked
autocomplete.addListener('place_changed', onPlaceChanged);
}

function onPlaceChanged (){
    var place = autocomplete.getPlace();

    // User did not select the prediction. Reset the input field or alert()
    if (!place.geometry){
        document.getElementById('id_address').placeholder = "Start typing...";
    }
    else{
        // console.log('place name=>', place.name)
    }
    // get the address components and assign them to the fields
    // console.log(place);
    var geocoder = new google.maps.Geocoder();
    var address = document.getElementById('id_address').value;
    // console.log(address)
    // result has address data and status is api call status
    geocoder.geocode({'address': address}, function(results, status){
        // console.log('results=', results); 
        // console.log('status=', status);
        if(status == google.maps.GeocoderStatus.OK){
            var latitude = results[0].geometry.location.lat();
            var longitude = results[0].geometry.location.lng();
            // console.log('lat=', latitude)
            // console.log('lng=', longitude)
            // places the values of lat and lng in the django form
            $('#id_latitude').val(latitude);
            $('#id_longitude').val(longitude);

            $('#id_address').val(address);
        }
    });

    // loop through the address components and assign other address data
    // console.log(place.address_components);
    for(var i=0; i<place.address_components.length; i++){
        for(var j=0; j<place.address_components[i].types.length; j++){
            // get country
            if(place.address_components[i].types[j] == 'country'){
                var country = place.address_components[i].long_name;
                $('#id_country').val(country);
            }
            // get state
            if(place.address_components[i].types[j] == 'administrative_area_level_1'){
                var state = place.address_components[i].long_name;
                $('#id_state').val(state);
            }
            // get city
            if(place.address_components[i].types[j] == 'locality'){
                var city = place.address_components[i].long_name;
                $('#id_city').val(city);
            }
            // get pincode
            if(place.address_components[i].types[j] == 'postal_code'){
                var pin_code = place.address_components[i].long_name;
                $('#id_pin_code').val(pin_code);
            }else{
                $('#id_pin_code').val("");
            }
        }
    } 
}

$(document).ready(function(){
    //add to cart
    $('.add_to_cart').on('click', function(e){
        e.preventDefault();
        
        food_id =  $(this).attr('data-id');
        url = $(this).attr('data-url');

        // send food id to view using ajax request
        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                // console.log(response)
                if(response.status == 'login_required'){
                    swal(response.message, '', 'info').then(function(){
                        window.location = '/login';
                    });
                }else if(response.status == 'Failed'){
                    swal(response.message, '', 'error');
                }else{
                    $('#cart-counter').html(response.cart_counter['cart_count'])
                    $('#qty-'+food_id).html(response.qty)

                    // sub total, tax and grand_total
                    var subtotal = response.cart_amount['subtotal'];
                    var tax = response.cart_amount['tax']
                    var grand_total = response.cart_amount['grand_total']
                    applyCartAmounts(subtotal, tax, grand_total)
                }
            }
        });
    });


    //place the cart item quantity on load
    $('.item_qty').each(function(){
        var the_id = $(this).attr('id');
        var qty = $(this).attr('data-qty');
        // console.log(qty)

        $('#'+the_id).html(qty)
    });

    //decrease cart
    $('.decrease_cart').on('click', function(e){
        e.preventDefault();
        
        food_id =  $(this).attr('data-id');
        url = $(this).attr('data-url');
        cart_id = $(this).attr('id');

        // send food id to view using ajax request
        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                // console.log(response)
                if(response.status == 'login_required'){
                    swal(response.message, '', 'info').then(function(){
                        window.location = '/login';
                    });
                }else if(response.status == 'Failed'){
                    swal(response.message, '', 'error');
                }else{
                    $('#cart-counter').html(response.cart_counter['cart_count'])
                    $('#qty-'+food_id).html(response.qty)

                    // sub total, tax and grand_total
                    var subtotal = response.cart_amount['subtotal'];
                    var tax = response.cart_amount['tax']
                    var grand_total = response.cart_amount['grand_total']
                    applyCartAmounts(subtotal, tax, grand_total)

                    if(window.location.pathname == '/cart/'){
                        removeCartItem(response.qty, cart_id);
                        checkEmptyCart();
                    }    
                }
            }
        });
    });

    // delte cart-tem
    $('.delete_cart').on('click', function(e){
        e.preventDefault();

        cart_id =  $(this).attr('data-id');
        url = $(this).attr('data-url');

        // send food id to view using ajax request
        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                // console.log(response)
                if(response.status == 'Failed'){
                    swal(response.message, '', 'error');
                }else{
                    $('#cart-counter').html(response.cart_counter['cart_count'])
                    swal(response.status, response.message, 'success')
                    removeCartItem(0, cart_id);
                    checkEmptyCart();

                    // sub total, tax and grand_total
                    var subtotal = response.cart_amount['subtotal'];
                    var tax = response.cart_amount['tax']
                    var grand_total = response.cart_amount['grand_total']
                    applyCartAmounts(subtotal, tax, grand_total)
                }
            }
        });
    });

    // delete cart item if qty is 0
    function removeCartItem(cartItemQty, cart_id){
        if(cartItemQty <= 0){
            // remove cart item
            document.getElementById("cart-item-"+cart_id).remove()
        }
    }

    // check if cart is empty
    function checkEmptyCart(){
        debugger
        var cart_counter = document.getElementById("cart-counter").innerHTML;
        if(cart_counter == 0){
            document.getElementById("empty-cart").style.display = "block";
        }
    }

    //apply cart amounts
    function applyCartAmounts(subtotal, tax, grand_total){
        if(window.location.pathname == '/cart/'){
            $('#subtotal').html(subtotal);
            $('#tax').html(tax);
            $('#total').html(grand_total);
        }
    }

    // add opening hours
    $('.add_hour').on('click', function(e){
        e.preventDefault()
        var day = document.getElementById('id_day').value
        var from_hour = document.getElementById('id_from_hour').value
        var to_hour = document.getElementById('id_to_hour').value
        var is_closed = document.getElementById('id_is_closed').checked
        var csrfToken = $('input[name=csrfmiddlewaretoken]').val()
        var url = document.getElementById('add_hour_url').value

        if( is_closed){
            is_closed = 'True'
            condition = "day != ''"
        }else{
            is_closed = 'False'
            condition = "day != '' && from_hour != '' && to_hour != ''"
        }
        if(eval(condition)){
            //add the entry
            $.ajax({
                type: 'POST',
                url: url,
                data: {
                    'day': day,
                    'from_hour': from_hour,
                    'to_hour': to_hour,
                    'is_closed': is_closed,
                    'csrfmiddlewaretoken': csrfToken,
                }, 
                success: function(response){
                    if(response.status == 'success'){
                        if(response.is_closed == 'Closed'){
                            html = '<tr id="hour-'+response.id +'"><td><b>'+response.day+'</b></td><td>Closed</td><td><a href="#" class="remove_hour" data-url="/vendor/openingHours/remove/'+ response.id +'/">Remove</a></td></tr>'
                        }else{
                            html = '<tr id="hour-'+response.id +'"><td><b>'+response.day+'</b></td><td>'+response.from_hour+' - '+response.to_hour+'</td><td><a href="#" class="remove_hour" data-url="/vendor/openingHours/remove/'+ response.id +'/">Remove</a></td></tr>'
                        }
                        $('.opening-hours').append(html)
                        document.getElementById('opening-hours').reset();
                    }else{
                        swal(response.message, '', 'error')
                    }
                }
            })
        }else{
            //raise error to fill all the fields
            swal('Please fill all the fields', '', 'info')
        }
    });

    //remove opening hours
    $(document).on('click', '.remove_hour', function(e){
        e.preventDefault()
        url = $(this).attr('data-url');

        $.ajax({
            url: url,
            type: 'GET',
            success: function(response){
                if(response.status == 'success'){
                    document.getElementById('hour-'+response.id).remove()
                }
            }
        })
    });


    // document ready closed

});