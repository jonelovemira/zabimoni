MAX_OPTIONS = 5;
// Add button click handler
        $(document).on('click', '.addButton', function() {
            var $template = $('#optionTemplate'),
                $clone    = $template
                                .clone()
                                .removeClass('hide')
                                .removeAttr('id')
                                .insertBefore($template),
                $email   = $clone.find('[name="email[]"]');

            // Add new field
            $('#fieldIconsForm').bootstrapValidator('addField', $email);
        })

        // Remove button click handler
        $(document).on('click', '.removeButton', function() {
            var $row    = $(this).parents('.form-group'),
                $email = $row.find('[name="email[]"]');

            // Remove element containing the option
            $row.remove();

            // Remove field
            $('#fieldIconsForm').bootstrapValidator('removeField', $email);
        })

        // Called after adding new field
        $(document).on('added.field.bv', function(e, data) {
            // data.field   --> The field name
            // data.element --> The new field element
            // data.options --> The new field options

            if (data.field === 'email[]') {
                if ($('#fieldIconsForm').find(':visible[name="email[]"]').length >= MAX_OPTIONS) {
                    $('#fieldIconsForm').find('.addButton').attr('disabled', 'disabled');
                }
            }
        })

        // Called after removing the field
        $(document).on('removed.field.bv', function(e, data) {
           if (data.field === 'option[]') {
                if ($('#fieldIconsForm').find(':visible[name="option[]"]').length < MAX_OPTIONS) {
                    $('#fieldIconsForm').find('.addButton').removeAttr('disabled');
                }
            }
        });