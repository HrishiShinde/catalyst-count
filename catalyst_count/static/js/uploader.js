class FileUpload {
    constructor(input) {
        this.input = input
        this.max_length = 1024 * 1024 * 10;
    }

    upload() {
        this.initFileUpload();
    }

    initFileUpload() {
        this.file = this.input.files[0];
        this.upload_file(0, null);
    }

    //upload file
    upload_file(start, model_id) {
        let end;
        let self = this;
        let existingPath = model_id;
        let formData = new FormData();
        let nextChunk = start + this.max_length + 1;
        let currentChunk = this.file.slice(start, nextChunk);
        let uploadedChunk = start + currentChunk.size
        if (uploadedChunk >= this.file.size) {
            end = 1;
        } else {
            end = 0;
        }
        let progress = 0;
        formData.append('file', currentChunk)
        formData.append('filename', this.file.name)
        formData.append('end', end)
        formData.append('existingPath', existingPath);
        formData.append('nextSlice', nextChunk);
        formData.append('filesize', this.file.size);
        $.ajaxSetup({
            headers: {
                "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
            }
        });
        $.ajax({
            xhr: function () {
                let xhr = new XMLHttpRequest();
                xhr.upload.addEventListener('progress', function (e) {
                    if (e.lengthComputable) {
                        if (self.file.size < self.max_length) {
                            progress = Math.round((e.loaded / e.total) * 100);
                        } else {
                            progress = Math.round((uploadedChunk / self.file.size) * 100);
                        }
                        var progressBar = document.querySelector('.progress-bar');
                        progressBar.style.width = progress + '%';
                        progressBar.setAttribute('aria-valuenow', progress);
                    }
                });
                return xhr;
            },

            url: '/upload/',
            type: 'POST',
            dataType: 'json',
            cache: false,
            processData: false,
            contentType: false,
            data: formData,
            error: function (xhr) {
                $('.textbox').text(xhr.statusText);
            },
            success: function (res) {
                if (nextChunk < self.file.size) {
                    // upload file in chunks
                    existingPath = res.existingPath
                    self.upload_file(nextChunk, existingPath);
                } else {
                    // upload complete
                    $('.textbox').text(res.data);
                }
            }
        });
    };
}
