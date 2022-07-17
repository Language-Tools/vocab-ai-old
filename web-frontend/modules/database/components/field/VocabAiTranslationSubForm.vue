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

    <div class="control">
      <Dropdown
        v-model="values.target_language"
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

    <div class="control">
      <Dropdown
        v-model="values.service"
        @input="translationServiceSelected"
      >
        <DropdownItem
          v-for="service in translationServices"
          :key="service"
          :name="service"
          :value="service"
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
  name: 'VocabAiTranslationSubForm',
  mixins: [form, fieldSubForm],
  data() {
    return {
      allowedValues: ['source_field_id'],
      values: {
        source_field_id: '',
        target_language: '',
        service: '',
      },
      selectedSourceFieldLanguage: '',
      languageList: [],
      translationServices: [],
    }
  },
  created() {
      // fetch language list
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
  methods: {
    isFormValid() {
      return true
    },
    async sourceFieldSelected() {
      console.log('source_field_id: ', this.values.source_field_id);
      const selectedField = this.$store.getters['field/get'](
          this.values.source_field_id
      );
      // console.log('selectedField: ', selectedField);
      this.selectedSourceFieldLanguage = selectedField.language;
      console.log('selectedSourceFieldLanguage: ', this.selectedSourceFieldLanguage);
      this.refreshServiceList();
    },    
    async languageSelected() {
      console.log('target language: ', this.values.target_language);
      this.refreshServiceList();
    },        
    async translationServiceSelected() {
      console.log('translation_service: ', this.values.translation_service);
    },            
    async refreshServiceList() {
      const source_language = this.selectedSourceFieldLanguage;
      const target_language = this.values.target_language;
      if(source_language != '' && target_language != '')  {
        CloudLanguageToolsService(this.$client).fetchTranslationServices(source_language, target_language).then((response) => {
          this.translationServices = response.data;
          console.log('translationServices: ', this.translationServices);
        });            
      }
    }    
  },
  computed: {
    tableFields() {
      // collect all fields, including primary field in this table
      const primaryField = this.$store.getters['field/getPrimary'];
      const fields = this.$store.getters['field/getAll']

      let allFields = [primaryField];
      allFields = allFields.concat(fields);

      const allLanguageFields = allFields.filter((f) => {
              return f.type == "language_text"
            });


      console.log('allLanguageFields: ', allLanguageFields);

      return allLanguageFields;
    },
  }  
}
</script>
