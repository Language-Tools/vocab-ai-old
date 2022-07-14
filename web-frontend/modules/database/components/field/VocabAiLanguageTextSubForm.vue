<template>
  <div>
    <div class="control">

      <Dropdown
        v-model="values.language"
        @input="languageSelected"
      >
        <DropdownItem
          v-for="language in languageList"
          :key="language.id"
          :name="language.name"
          :value="language.id"
          icon="font"
        ></DropdownItem>
      </Dropdown>

    </div>
  </div>
</template>


<script>
import form from '@baserow/modules/core/mixins/form'

import fieldSubForm from '@baserow/modules/database/mixins/fieldSubForm'

import CloudLanguageToolsService from '@baserow/modules/database/services/cloudlanguagetools'

export default {
  name: 'FieldTextSubForm',
  mixins: [form, fieldSubForm],
  data() {
    return {
      allowedValues: ['language'],
      values: {
        language: '',
      },
      languageList: [],
    }
  },
  created() {
      CloudLanguageToolsService(this.$client).fetchAllLanguages().then((response) => {
        let result = [];
        for (const language_id in response.data) {
          result.push({
            id: language_id,
            name: response.data[language_id]
          });
        }    
        console.log("result: ", result);
        this.languageList = result;
      });
  },
  computed: {
  },  
  methods: {
    async languageSelected() {
      console.log('language: ', this.values.language);
    },        
    isFormValid() {
      return true
    },
  },
}
</script>
