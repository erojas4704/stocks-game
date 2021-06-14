/**
 * Returns a promise awaiting user interaction. The promise returns an object with the action of the button that was pressed, as well as any form values in the modal.
 * @param {string} title 
 * @param {string} body 
 * @param  {...string} options Modal options can be a simple string or an object with label and class fields.
 */
function openModal(title, body, ...options) {
    createModal();

    return new Promise((resolve, reject) => {
        $("#modal_").modal();
        $("#modal_label").html(title);
        $(".modal-body").html(body);

        //Automatically append a close button.
        $(".modal-footer")
        .empty()
        .append(`<button type="button" class="btn btn-secondary" data-response="close" data-dismiss="modal">Close</button>`)

        let keepOpen = options.keepOpen || false;

        options.forEach(o => {
            //If it's a string, use generic.
            //If it's an object, figure it out.
            if (typeof(o) == "string") {
                $(".modal-footer").append(`<button type="button" class="btn btn-secondary" data-dismiss="modal" data-response="${o.toLowerCase()}">${o}</button>`)
            } 
            else {
                let action = o.label.toLowerCase();
                if(o.action){
                    action = o.action;
                }
                $(".modal-footer").append(`<button type="button" class="btn ${o.class}" ${o.keepOpen? 'data-keepOpen="true"': 'data-dismiss="modal"'} data-response="${action}">${o.label}</button>`)
            }
        });

        $("#modal_").on("keypress", e => {
            if(e.which === 13){
                //Simulate a click on the right most button 
                $(".modal-footer button:last").click();
            }
        })

        $(".modal-footer").on("click", "button", e => {
            $("#modal_").off("keypress");

            let values = {};
    
            $('.modal-body input,.modal-body select,.modal-body textarea').each((i, el) => {
                values[el.name] = $(el).val();
            });

            let response = {
                action: $(e.target).data("response"),
                form: values
            };
            
            resolve(response);
        });
    });
}

function alterModal(title, body){
    $("#modal_label").html(title);
    $(".modal-body").html(body);
    $(".modal-footer").empty();
}

function lockModal(){
    $(".close").hide();
    $("#modal_").css("pointer-events", "none");
}

function unlockModal(){
    $(".close").show();
    $("#modal_").css("pointer-events", "auto");
}

function createModal() {
    if($("#modal_").length > 0){
        return; //modal exists
    }

    $('body').append(`
    <!-- Modal -->
    <div class="modal fade" id="modal_" tabindex="-1" role="dialog" aria-labelledby="modal_label"
        aria-hidden="true">
        <div class="modal-dialog" role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="modal_label">label</h5>
                    <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                    </button>
                </div>
                <div class="modal-body">
                    body
                </div>
                <div class="modal-footer">
                    <!-- <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
                    <button type="button" class="btn btn-danger">Delete</button> -->
                </div>
            </div>
        </div>
    </div>
    `);
}