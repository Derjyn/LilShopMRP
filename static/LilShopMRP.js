// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
// LilShopMRP.js
// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

window.onload = function() {
    $('#link-dashboard,#link-products,#link-inventory,#link-suppliers,#link-sales,#link-forecast,#link-orders').on('mouseenter', function() {
        $(this).children('.icon-navbar').addClass('icon-tada');
    });
      
    $('#link-dashboard,#link-products,#link-inventory,#link-suppliers,#link-sales,#link-forecast,#link-orders').on('mouseleave', function() {
        $(this).children('.icon-navbar').removeClass('icon-tada');
    });

    $('#modal-edit-product').on('show.bs.modal', function (event) {
        const button = event.relatedTarget
        const recipient = button.getAttribute('data-product-id')

        console.log(recipient)
        
        $.get('/get_product/' + recipient, function(data) {
            $('.modal-content').html(data);
        });
    });
};
