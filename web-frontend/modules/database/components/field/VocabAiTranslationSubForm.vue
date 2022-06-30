<template>
  <div>
    <div class="control">

      <Dropdown
        v-model="values.source_field_id"
        @input="sourceFieldSelected"
      >
        <DropdownItem
          v-for="field in tableFields"
          :key="field.id"
          :name="field.name"
          :value="field.id"
          :icon="field.icon"
        ></DropdownItem>
      </Dropdown>

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
    async sourceFieldSelected() {
      console.log('source_field_id: ', this.values.source_field_id);
    },    
  },
  computed: {
    tableFields() {
      const primaryField = this.$store.getters['field/getPrimary'];
      const fields = this.$store.getters['field/getAll']

      let allFields = [primaryField];
      allFields = allFields.concat(fields);

      return allFields;
    },
  }  
}
</script>
