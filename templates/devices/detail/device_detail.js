provided_data = {{ provided_data|safe }};

function loadAdditionalData(adata) {
    $.ajax({
        method: "GET",
            url: "{% url 'device-details-json' device_id %}",
        }).done(function(data) {
            if (data.formatted_entries) {
                adata.provided_data = data.formatted_entries;
            }
            if (data.raw_entries) {
                adata.raw_provided_data = data.raw_entries;
            }
        }).fail(function() {
    });
}

function deviceDetail() {
    return {
        provided_data: provided_data,
        raw_provided_data: [],
        onLoad() {
            loadAdditionalData(this);
        },
        storedAt() {
            if (this.provided_data && this.provided_data.length > 0) {
                return this.provided_data[0].stored_at;
            } else {
                return "";
            }
        }
    }
}
