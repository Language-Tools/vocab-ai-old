import { FieldType } from '@baserow/modules/database/fieldTypes'

import GridViewFieldText from '@baserow/modules/database/components/view/grid/fields/GridViewFieldText'
import RowEditFieldText from '@baserow/modules/database/components/row/RowEditFieldText'
import VocabAiTranslationSubForm from '@baserow/modules/database/components/field/VocabAiTranslationSubForm'
import FunctionalGridViewFieldText from '@baserow/modules/database/components/view/grid/fields/FunctionalGridViewFieldText'

export class TranslationFieldType extends FieldType {
  static getType() {
    return 'translation'
  }

  getIconClass() {
    return 'list-ol'
  }

  getName() {
    return 'Translation'
  }

  getFormComponent() {
    return VocabAiTranslationSubForm
  }

  getGridViewFieldComponent() {
    return GridViewFieldText
  }

  getRowEditFieldComponent() {
    return RowEditFieldText
  }

  getFunctionalGridViewFieldComponent() {
    return FunctionalGridViewFieldText
  }

}