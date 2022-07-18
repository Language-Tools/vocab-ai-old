import CloudLanguageToolsService from '@baserow/modules/database/services/cloudlanguagetools'

export const state = () => ({
  allLanguages: [],
  allTranslationOptions: [],
  allTranslationServices: [],
})

export const mutations = {
  SET_ALL_LANGUAGES(state, allLanguages) {
    state.allLanguages = allLanguages;
  },
  SET_ALL_TRANSLATION_OPTIONS(state, allTranslationOptions) {
    state.allTranslationOptions = allTranslationOptions;
  },
  SET_ALL_TRANSLATION_SERVICES(state, allTranslationServices) {
    state.allTranslationServices = allTranslationServices;
  },  
}

export const actions = {

  async fetchAll({ dispatch}) {
    console.log('store/cloudlanguagetools fetchAll');
    await dispatch('fetchAllLanguages');
    await dispatch('fetchAllTranslationOptions');
  },

  async fetchAllLanguages({ commit, getters, dispatch }, table) {
    console.log('store/cloudlanguagetools fetchAllLanguages');
    return new Promise((resolve, reject) => {
        // const { data } = await CloudLanguageToolsService(this.$client).fetchAllLanguages()
        CloudLanguageToolsService(this.$client).fetchAllLanguages().then((response) => {
            let languagesArray = [];
            for (const language_id in response.data) {
                languagesArray.push({
                id: language_id,
                name: response.data[language_id]
                });
            }
            commit('SET_ALL_LANGUAGES', languagesArray);
            resolve();
        });
    });
  },

  async fetchAllTranslationOptions({ commit, getters, dispatch }, table) {
    console.log('store/cloudlanguagetools fetchAllTranslationOptions');
    return new Promise((resolve, reject) => {
        CloudLanguageToolsService(this.$client).fetchAllTranslationOptions().then((response) => {
            commit('SET_ALL_TRANSLATION_OPTIONS', response.data);
            // get list of all services
            const services = Object.keys(response.data.reduce((result, key) => {
                // console.log('result: ', result, 'key: ', key);
                result[key['service']] = true;
                return result;
            }, {}));
            commit('SET_ALL_TRANSLATION_SERVICES', services);
            resolve();
        });
    });
  },  


}

export const getters = {
    allLanguages(state) {
        return state.allLanguages;
    },
    allTranslationServices(state) {
        return state.allTranslationServices;
    },
    translationServicesForLanguages: (state) => (sourceLanguage, targetLanguage) => {
        const sourceLanguageServices = Object.keys(state.allTranslationOptions.filter((entry) => entry['language_code'] == sourceLanguage).
            reduce((result, entry) => {
                result[entry['service']] = true;
                return result;
            }, {}));
        const targetLanguageServices = Object.keys(state.allTranslationOptions.filter((entry) => entry['language_code'] == targetLanguage).
            reduce((result, entry) => {
                result[entry['service']] = true;
                return result;
            }, {}));            
        
        const commonServices = sourceLanguageServices.filter(value => targetLanguageServices.includes(value));
        return commonServices.sort((a, b) => a.localeCompare(b));
      },    
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
}
