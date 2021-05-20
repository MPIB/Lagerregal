initialDevice = {{ device|safe }};

function createDevice(adata) {
    adata.isLoading = true;
    $.ajax({
        method: "POST",
        url: "{% url 'init-automatic-device' %}",
        data: {
            "name": adata.name,
            "department": adata.department,
            "device_type": adata.deviceType,
            "operating_system": adata.operatingSystem,
        },
    }).done(function(data) {
        console.log(data);
        adata.isLoading = false;
        adata.device = data;

        history.replaceState(null, '', "?id=" + data.id);
    }).fail(function() {
        adata.isLoading = false;
    });
}

function deviceForm() {
    return {
        device: initialDevice,
        isLoading: false,
        name: "",
        department: "",
        deviceType: "",
        operatingSystem: "",
        formLoaded() {
            if (this.device.id) {
                this.name = this.device.name;
                this.department = this.device.department;
                this.deviceType = this.device.devicetype;
                this.operatingSystem = this.device.operating_system || "";
            } else {
                this.operatingSystem = this.$refs.operatingSystem.value;
            }
        },
        canInitialize() {
            return this.name && this.department && this.deviceType && this.operatingSystem;
        },
        hasDevice() {
            return this.device.pk !== undefined || this.device.id !== undefined;
        },
        createDevice() {
            createDevice(this);
        },
    }
}
