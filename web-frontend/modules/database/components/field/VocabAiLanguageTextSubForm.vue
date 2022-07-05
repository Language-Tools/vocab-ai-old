<template>
  <div>
    <div class="control">
      <div class="control__elements">
        <input
          ref="language"
          v-model="values.language"
          type="text"
          class="input"
          :placeholder="Language"
        />
      </div>
    </div>
  </div>
</template>


<script>
import form from '@baserow/modules/core/mixins/form'

import fieldSubForm from '@baserow/modules/database/mixins/fieldSubForm'

export default {
  name: 'FieldTextSubForm',
  mixins: [form, fieldSubForm],
  data() {
    return {
      allowedValues: ['language'],
      values: {
        language: '',
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
