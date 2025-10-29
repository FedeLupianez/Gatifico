# Script de limpieza para linux
echo "Iniciando limpieza..."

# Eliminar archivos .log, .pyz y .pyc del directorio actual
rm -f ./*.log ./*.pyz ./*.pyc

echo "Borrando minerales en el mapa..."
echo " " >"src/resources/Data/Saved/minerals_in_map.txt"

echo "Borrando cofres..."
echo '{"chest_1": [], "chest_2": [], "chest_3": []}' >"src/resources/Data/Saved/Chests_Data.json"

echo "Borrando la partida guardada..."
echo '{"player": {"position": {"center_x": 677.9216478540386, "center_y": 1244.99966327372}, "inventory": {}, "lifes": 5, "healt": 100}, "scene": "LABORATORY", "time_stamp": 0}' >"src/resources/Data/Saved/saved.json"

echo "Limpieza completada."
