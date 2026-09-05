# Gson deserialises the question bundle and the local store by reflection, so
# the model classes and their fields must survive R8.
-keep class com.drivers.test.model.** { *; }
-keep class com.drivers.test.repository.** { *; }

# Gson's generic TypeToken needs signature metadata (R8 full mode strips it).
-keepattributes Signature, InnerClasses, EnclosingMethod, *Annotation*
-keep class com.google.gson.reflect.TypeToken { *; }
-keep class * extends com.google.gson.reflect.TypeToken
-keep,allowobfuscation,allowshrinking class com.google.gson.reflect.TypeToken
-keep,allowobfuscation,allowshrinking class * extends com.google.gson.reflect.TypeToken
-dontwarn sun.misc.Unsafe
