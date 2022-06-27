<template>
  <div>
    <div class="control">
      <div class="control__elements">
        <input
          ref="source_field_id"
          v-model.number="values.source_field_id"
          type="number"
          class="input"
          placeholder="Field to translate"
        />
      </div>
    </div>
  </div>
</template>

<script>
import form from '@baserow/modules/core/mixins/form'

import fieldSubForm from '@baserow/modules/database/mixins/fieldSubForm'

export default {
  name: 'VocabAiTranslationSubForm',
  mixins: [form, fieldSubForm],
  data() {
    return {
      allowedValues: ['source_field_id'],
      values: {
        source_field_id: '',
      },
    }
  },
  methods: {
    isFormValid() {
      return true
    },
  },
}
</script>
