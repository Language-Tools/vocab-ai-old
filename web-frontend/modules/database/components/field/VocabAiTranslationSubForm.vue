<template>
  <div>
    <div class="control">
      <div class="control__elements">
        <input
          ref="source_field"
          v-model="values.source_field"
          type="text"
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
      allowedValues: ['source_field'],
      values: {
        source_field: '',
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
